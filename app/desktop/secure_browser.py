"""Agente 19 Desktop com navegador seguro.

A aplicacao desktop nao solicita nem processa credenciais do SEI. O SEI e
aberto somente pela URL oficial, em navegador/janela separada controlada pelo
usuario. O painel do Agente 19 fala apenas com o backend local em 127.0.0.1.
"""

from __future__ import annotations

import base64
import json
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from app.core.config import get_settings
from app.core.safety import assert_safe_environment
from app.dashboard.local_app import run as run_dashboard


SEI_OFFICIAL_URL = "https://sei.go.gov.br/sei/"
LOCAL_BACKEND_ORIGIN = "http://127.0.0.1:8000"
SECURITY_NOTICE = (
    "O login é realizado exclusivamente na página oficial do SEI. "
    "O Agente 19 não captura senha, cookie, sessão ou credenciais "
    "e não pratica atos oficiais."
)

ALLOWED_ENDPOINTS = {
    "/api/import-text",
    "/api/import-pdf",
    "/api/generate-draft",
    "/api/triage-local",
}
CREDENTIAL_KEY_FRAGMENTS = (
    "senha",
    "password",
    "cookie",
    "session",
    "token",
    "authorization",
    "credencial",
    "usuario_sei",
    "login_sei",
)
CREDENTIAL_VALUE_PATTERN = re.compile(
    r"\b(senha|password|token|cookie|credencial)\s*[:=]", re.IGNORECASE
)


@dataclass(frozen=True)
class FieldSpec:
    name: str
    label: str


AGENT_INPUT_FIELDS = (
    FieldSpec("processo_sei", "Processo SEI"),
    FieldSpec("usuario_local", "Operador local (não é usuário do SEI)"),
    FieldSpec("titulo", "Título"),
)


class CredentialPolicyViolation(ValueError):
    """Erro quando algum fluxo tenta carregar credenciais no Agente 19."""


def validate_backend_origin(origin: str) -> str:
    """Garante que o desktop fale apenas com 127.0.0.1."""
    parsed = urllib.parse.urlparse(origin)
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1":
        raise ValueError("Backend do Agente 19 deve usar apenas http://127.0.0.1.")
    if parsed.username or parsed.password:
        raise ValueError("URL do backend local nao pode conter credenciais.")
    port = parsed.port or 80
    return f"http://127.0.0.1:{port}"


def ensure_no_credential_payload(payload: dict[str, Any]) -> None:
    """Bloqueia campos ou valores com indicio claro de credencial."""
    for key, value in payload.items():
        normalized_key = str(key).lower()
        if any(fragment in normalized_key for fragment in CREDENTIAL_KEY_FRAGMENTS):
            raise CredentialPolicyViolation(
                f"Campo proibido para o Agente 19 Desktop: {key}."
            )
        if isinstance(value, dict):
            ensure_no_credential_payload(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    ensure_no_credential_payload(item)
                elif isinstance(item, str) and CREDENTIAL_VALUE_PATTERN.search(item):
                    raise CredentialPolicyViolation(
                        "Conteudo com possivel credencial foi bloqueado."
                    )
        elif isinstance(value, str) and CREDENTIAL_VALUE_PATTERN.search(value):
            raise CredentialPolicyViolation(
                "Conteudo com possivel credencial foi bloqueado."
            )


def open_official_sei(open_browser: Callable[[str], Any] | None = None) -> bool:
    """Abre somente a URL oficial do SEI para login direto pelo usuario."""
    opener = open_browser or webbrowser.open
    return bool(opener(SEI_OFFICIAL_URL))


def open_local_panel(open_browser: Callable[[str], Any] | None = None) -> bool:
    """Abre o painel web local do Agente 19, sem tocar no SEI."""
    opener = open_browser or webbrowser.open
    return bool(opener(LOCAL_BACKEND_ORIGIN))


def start_backend_if_needed(timeout_seconds: float = 3.0) -> bool:
    """Inicia o backend local em thread daemon quando ele ainda nao esta ativo."""
    if _backend_is_healthy():
        return False

    settings = get_settings()
    thread = threading.Thread(
        target=run_dashboard,
        kwargs={"host": settings.app_host, "port": settings.app_port},
        name="agente19-backend-local",
        daemon=True,
    )
    thread.start()

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if _backend_is_healthy():
            return True
        time.sleep(0.1)
    return True


def analyze_text_via_backend(
    *,
    titulo: str,
    texto: str,
    processo_sei: str = "",
    usuario_local: str = "",
    backend_origin: str = LOCAL_BACKEND_ORIGIN,
) -> dict[str, Any]:
    payload = {
        "titulo": titulo,
        "texto": texto,
        "processo_sei": processo_sei,
        "usuario_local": usuario_local,
        "origem": "desktop_navegador_seguro",
    }
    return _post_json("/api/import-text", payload, backend_origin=backend_origin)


def analyze_pdf_via_backend(
    *,
    filename: str,
    content: bytes,
    titulo: str,
    processo_sei: str = "",
    usuario_local: str = "",
    backend_origin: str = LOCAL_BACKEND_ORIGIN,
) -> dict[str, Any]:
    payload = {
        "filename": Path(filename).name,
        "content_base64": base64.b64encode(content).decode("ascii"),
        "titulo": titulo,
        "processo_sei": processo_sei,
        "usuario_local": usuario_local,
        "origem": "desktop_navegador_seguro",
    }
    return _post_json("/api/import-pdf", payload, backend_origin=backend_origin)


def generate_draft_via_backend(
    *,
    assunto: str,
    resumo: str,
    processo_sei: str = "",
    usuario_local: str = "",
    unidade_destino: str = "",
    destinatario: str = "",
    tipo_minuta: str = "",
    prazo: str = "",
    evento: str = "",
    backend_origin: str = LOCAL_BACKEND_ORIGIN,
) -> dict[str, Any]:
    payload = {
        "assunto": assunto,
        "resumo": resumo,
        "processo_sei": processo_sei,
        "usuario_local": usuario_local,
        "unidade_destino": unidade_destino,
        "destinatario": destinatario,
        "tipo_minuta": tipo_minuta,
        "prazo": prazo,
        "evento": evento,
        "origem": "desktop_navegador_seguro",
    }
    return _post_json("/api/generate-draft", payload, backend_origin=backend_origin)


def triage_via_backend(
    *,
    assunto: str,
    texto: str,
    processo_sei: str = "",
    usuario_local: str = "",
    backend_origin: str = LOCAL_BACKEND_ORIGIN,
) -> dict[str, Any]:
    payload = {
        "assunto": assunto,
        "texto": texto,
        "processo_sei": processo_sei,
        "usuario_local": usuario_local,
        "origem": "desktop_navegador_seguro",
    }
    return _post_json("/api/triage-local", payload, backend_origin=backend_origin)


def format_analysis_result(payload: dict[str, Any]) -> str:
    """Formata a resposta local para copiar/colar fora do SEI."""
    resultado = payload.get("resultado", {}) if isinstance(payload, dict) else {}
    evento = resultado.get("evento", {}) if isinstance(resultado, dict) else {}
    prazo = resultado.get("prazo", {}) if isinstance(resultado, dict) else {}
    resumo = str(resultado.get("resumo_executivo", "")).strip()
    tipo = _infer_tipo_provavel(resultado)
    providencia = _suggest_providence(payload)
    pendentes = payload.get("campos_pendentes", []) if isinstance(payload, dict) else []

    return "\n".join(
        [
            "Agente 19 - Analise preliminar",
            f"Status: {payload.get('status', '')}",
            f"Tipo provavel: {tipo}",
            f"Revisao humana: {'obrigatoria' if payload.get('revisao_humana_obrigatoria') else 'nao informada'}",
            f"Confianca: {payload.get('confianca', '')}",
            "",
            "Resumo:",
            resumo or "Resumo nao gerado.",
            "",
            f"Evento: {_format_event(evento)}",
            f"Prazo: {_format_deadline(prazo)}",
            f"Providencia sugerida: {providencia}",
            f"Campos pendentes: {', '.join(map(str, pendentes)) if pendentes else 'nenhum'}",
            "",
            "Observacao: atos oficiais no SEI devem ser praticados manualmente pelo usuario logado.",
        ]
    )


def format_draft_result(payload: dict[str, Any]) -> str:
    """Formata a minuta local para copia manual."""
    resultado = payload.get("resultado", {}) if isinstance(payload, dict) else {}
    alertas = resultado.get("alertas", []) if isinstance(resultado, dict) else []
    pendentes = payload.get("campos_pendentes", []) if isinstance(payload, dict) else []
    return "\n".join(
        [
            "Agente 19 - Minuta local preliminar",
            f"Tipo: {resultado.get('tipo_minuta', '')}",
            f"Confianca: {payload.get('confianca', '')}",
            (
                "Revisao humana: "
                f"{'obrigatoria' if payload.get('revisao_humana_obrigatoria') else 'nao informada'}"
            ),
            "",
            str(resultado.get("texto", "")).strip(),
            "",
            f"Providencia sugerida: {resultado.get('providencia_sugerida', '')}",
            f"Campos pendentes: {', '.join(map(str, pendentes)) if pendentes else 'nenhum'}",
            f"Alertas: {' | '.join(map(str, alertas)) if alertas else 'nenhum'}",
            "",
            (
                "Observacao: copie para o SEI somente apos revisar. "
                "O Agente 19 nao assina nem tramita."
            ),
        ]
    )


def format_triage_result(payload: dict[str, Any]) -> str:
    resultado = payload.get("resultado", {}) if isinstance(payload, dict) else {}
    pendentes = payload.get("campos_pendentes", []) if isinstance(payload, dict) else []
    return "\n".join(
        [
            "Agente 19 - Triagem local",
            f"Interesse 19 CRPM: {resultado.get('interesse_19crpm', '')}",
            f"Unidade sugerida: {resultado.get('unidade_sugerida') or 'indefinida'}",
            f"Tipo de minuta: {resultado.get('tipo_minuta_sugerido') or 'indefinido'}",
            f"Providencia: {resultado.get('providencia_sugerida', '')}",
            f"Regra aplicada: {resultado.get('regra_aplicada') or 'nenhuma'}",
            f"Confianca: {payload.get('confianca', '')}",
            f"Campos pendentes: {', '.join(map(str, pendentes)) if pendentes else 'nenhum'}",
            "",
            str(resultado.get("justificativa", "")).strip(),
            "",
            "Observacao: se nao houver regra clara, nao direcione automaticamente.",
        ]
    )


def run() -> None:
    """Sobe backend local e abre a janela desktop."""
    assert_safe_environment(get_settings())
    start_backend_if_needed()
    app = SecureDesktopApp()
    app.mainloop()


class SecureDesktopApp:
    """Janela Tkinter local do Agente 19."""

    def __init__(self, backend_origin: str = LOCAL_BACKEND_ORIGIN) -> None:
        import tkinter as tk
        from tkinter import scrolledtext

        self.tk = tk
        self.backend_origin = validate_backend_origin(backend_origin)
        self.root = tk.Tk()
        self.root.title("Agente 19 Desktop")
        self.root.geometry("1120x720")
        self.root.minsize(860, 560)
        
        # Forca a janela a saltar para a frente (rouba o foco)
        self.root.attributes("-topmost", True)
        self.root.update()
        self.root.attributes("-topmost", False)
        self.root.lift()
        self.root.focus_force()
        self.pdf_path: Path | None = None
        self.last_result = ""
        self.last_analysis: dict[str, Any] | None = None

        self.notice_var = tk.StringVar(value=SECURITY_NOTICE)
        self.status_var = tk.StringVar(value="Backend local: 127.0.0.1")
        self.fields: dict[str, Any] = {}

        self._build_layout(scrolledtext)

    def mainloop(self) -> None:
        self.root.mainloop()

    def _build_layout(self, scrolledtext: Any) -> None:
        tk = self.tk
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(1, weight=1)

        notice = tk.Message(
            self.root,
            textvariable=self.notice_var,
            width=1040,
            bg="#fff6db",
            fg="#3b3425",
            padx=12,
            pady=10,
        )
        notice.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 8))

        sei_frame = tk.LabelFrame(self.root, text="SEI oficial")
        sei_frame.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=8)
        sei_frame.columnconfigure(0, weight=1)

        tk.Label(
            sei_frame,
            text=(
                "Abra o SEI pela URL oficial. O login acontece somente na pagina "
                "oficial carregada pelo navegador do usuario."
            ),
            justify="left",
            wraplength=360,
        ).grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        tk.Button(
            sei_frame,
            text="Abrir SEI oficial",
            command=open_official_sei,
        ).grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        tk.Button(
            sei_frame,
            text="Abrir painel web local",
            command=open_local_panel,
        ).grid(row=2, column=0, sticky="ew", padx=12, pady=6)
        tk.Label(
            sei_frame,
            text=(
                "Copie manualmente o trecho do SEI ou exporte o PDF manualmente. "
                "Depois use o painel do Agente 19 ao lado."
            ),
            justify="left",
            wraplength=360,
        ).grid(row=3, column=0, sticky="new", padx=12, pady=(12, 6))

        agent_frame = tk.LabelFrame(self.root, text="Agente 19")
        agent_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=8)
        agent_frame.columnconfigure(1, weight=1)
        agent_frame.rowconfigure(4, weight=1)
        agent_frame.rowconfigure(8, weight=1)

        for row, field in enumerate(AGENT_INPUT_FIELDS):
            tk.Label(agent_frame, text=field.label).grid(
                row=row, column=0, sticky="w", padx=12, pady=5
            )
            entry = tk.Entry(agent_frame)
            entry.grid(row=row, column=1, sticky="ew", padx=12, pady=5)
            self.fields[field.name] = entry

        tk.Label(agent_frame, text="Texto copiado manualmente").grid(
            row=3, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 5)
        )
        self.text_input = scrolledtext.ScrolledText(agent_frame, height=8, wrap="word")
        self.text_input.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=12, pady=5)

        buttons = tk.Frame(agent_frame)
        buttons.grid(row=5, column=0, columnspan=2, sticky="ew", padx=12, pady=8)
        for index in range(6):
            buttons.columnconfigure(index, weight=1)
        tk.Button(buttons, text="Analisar texto", command=self._analyze_text).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        tk.Button(buttons, text="Selecionar PDF", command=self._select_pdf).grid(
            row=0, column=1, sticky="ew", padx=6
        )
        tk.Button(buttons, text="Analisar PDF", command=self._analyze_pdf).grid(
            row=0, column=2, sticky="ew", padx=6
        )
        tk.Button(buttons, text="Triagem local", command=self._triage_local).grid(
            row=0, column=3, sticky="ew", padx=(6, 0)
        )
        tk.Button(buttons, text="Gerar minuta", command=self._generate_draft).grid(
            row=0, column=4, sticky="ew", padx=(6, 0)
        )
        tk.Button(buttons, text="Copiar resultado", command=self._copy_result).grid(
            row=0, column=5, sticky="ew", padx=(6, 0)
        )

        self.pdf_label_var = tk.StringVar(value="Nenhum PDF selecionado.")
        tk.Label(agent_frame, textvariable=self.pdf_label_var, anchor="w").grid(
            row=6, column=0, columnspan=2, sticky="ew", padx=12, pady=2
        )
        tk.Label(agent_frame, text="Resultado").grid(
            row=7, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 5)
        )
        self.result_output = scrolledtext.ScrolledText(agent_frame, height=12, wrap="word")
        self.result_output.grid(
            row=8, column=0, columnspan=2, sticky="nsew", padx=12, pady=5
        )
        tk.Label(agent_frame, textvariable=self.status_var, anchor="w").grid(
            row=9, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 12)
        )

    def _payload_base(self) -> dict[str, str]:
        return {name: entry.get().strip() for name, entry in self.fields.items()}

    def _analyze_text(self) -> None:
        payload = self._payload_base()
        texto = self.text_input.get("1.0", "end").strip()
        try:
            result = analyze_text_via_backend(
                titulo=payload["titulo"],
                texto=texto,
                processo_sei=payload["processo_sei"],
                usuario_local=payload["usuario_local"],
                backend_origin=self.backend_origin,
            )
            self.last_analysis = result
            self._show_result(format_analysis_result(result))
        except Exception as exc:
            self._show_error(exc)

    def _select_pdf(self) -> None:
        from tkinter import filedialog

        selected = filedialog.askopenfilename(
            title="Selecionar PDF exportado manualmente do SEI",
            filetypes=[("PDF", "*.pdf")],
        )
        if not selected:
            return
        self.pdf_path = Path(selected)
        self.pdf_label_var.set(self.pdf_path.name)

    def _analyze_pdf(self) -> None:
        if not self.pdf_path:
            self.status_var.set("Selecione um PDF exportado manualmente.")
            return
        payload = self._payload_base()
        try:
            result = analyze_pdf_via_backend(
                filename=self.pdf_path.name,
                content=self.pdf_path.read_bytes(),
                titulo=payload["titulo"],
                processo_sei=payload["processo_sei"],
                usuario_local=payload["usuario_local"],
                backend_origin=self.backend_origin,
            )
            self.last_analysis = result
            self._show_result(format_analysis_result(result))
        except Exception as exc:
            self._show_error(exc)

    def _generate_draft(self) -> None:
        if not self.last_analysis:
            self.status_var.set("Analise texto ou PDF antes de gerar minuta.")
            return
        payload = self._payload_base()
        resultado = self.last_analysis.get("resultado", {})
        event = resultado.get("evento", {}) if isinstance(resultado, dict) else {}
        deadline = resultado.get("prazo", {}) if isinstance(resultado, dict) else {}
        prazo = _format_deadline(deadline) if deadline.get("ha_prazo") else ""
        evento = _format_event(event) if event.get("ha_evento") else ""
        try:
            draft = generate_draft_via_backend(
                assunto=payload["titulo"],
                resumo=str(resultado.get("resumo_executivo", "")),
                processo_sei=payload["processo_sei"],
                usuario_local=payload["usuario_local"],
                prazo=prazo,
                evento=evento,
                backend_origin=self.backend_origin,
            )
            self._show_result(format_draft_result(draft))
        except Exception as exc:
            self._show_error(exc)

    def _triage_local(self) -> None:
        if not self.last_analysis:
            self.status_var.set("Analise texto ou PDF antes de executar triagem.")
            return
        payload = self._payload_base()
        resultado = self.last_analysis.get("resultado", {})
        try:
            triage = triage_via_backend(
                assunto=payload["titulo"],
                texto=str(resultado.get("resumo_executivo", "")),
                processo_sei=payload["processo_sei"],
                usuario_local=payload["usuario_local"],
                backend_origin=self.backend_origin,
            )
            self._show_result(format_triage_result(triage))
        except Exception as exc:
            self._show_error(exc)

    def _copy_result(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_result)
        self.status_var.set("Resultado copiado para a area de transferencia.")

    def _show_result(self, text: str) -> None:
        self.last_result = text
        self.result_output.delete("1.0", "end")
        self.result_output.insert("1.0", text)
        self.status_var.set("Analise local concluida. Revise antes de usar.")

    def _show_error(self, exc: Exception) -> None:
        message = str(exc) or exc.__class__.__name__
        self.status_var.set(f"Falha: {message}")


def _post_json(
    endpoint: str,
    payload: dict[str, Any],
    *,
    backend_origin: str = LOCAL_BACKEND_ORIGIN,
) -> dict[str, Any]:
    if endpoint not in ALLOWED_ENDPOINTS:
        raise ValueError("Endpoint local nao autorizado.")
    origin = validate_backend_origin(backend_origin)
    ensure_no_credential_payload(payload)
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{origin}{endpoint}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body)
    return parsed if isinstance(parsed, dict) else {}


def _backend_is_healthy() -> bool:
    try:
        with urllib.request.urlopen(f"{LOCAL_BACKEND_ORIGIN}/health", timeout=0.5) as resp:
            return 200 <= resp.status < 300
    except (OSError, urllib.error.URLError):
        return False


def _infer_tipo_provavel(resultado: dict[str, Any]) -> str:
    status_leitura = str(resultado.get("status_leitura", ""))
    if status_leitura == "ocr_necessario":
        return "PDF escaneado ou sem texto extraivel"
    evento = resultado.get("evento", {}) if isinstance(resultado, dict) else {}
    prazo = resultado.get("prazo", {}) if isinstance(resultado, dict) else {}
    if evento.get("ha_evento") and prazo.get("ha_prazo"):
        return "Demanda com evento e prazo"
    if evento.get("ha_evento"):
        return "Demanda com possivel evento"
    if prazo.get("ha_prazo"):
        return "Demanda com possivel prazo"
    if resultado.get("file_hash"):
        return "PDF administrativo para revisao"
    return "Texto administrativo para revisao"


def _suggest_providence(payload: dict[str, Any]) -> str:
    actions = payload.get("acoes_sugeridas", []) if isinstance(payload, dict) else []
    if "REVISAR_OCR" in actions:
        return "Executar OCR ou obter PDF pesquisavel antes de concluir."
    if "REVISAR_EVENTO" in actions and "REVISAR_PRAZO" in actions:
        return "Revisar evento e prazo; depois decidir manualmente a providencia no SEI."
    if "REVISAR_EVENTO" in actions:
        return "Revisar dados do evento e avaliar lancamento manual na agenda."
    if "REVISAR_PRAZO" in actions:
        return "Revisar prazo e acompanhar manualmente a providencia."
    return "Revisar o resumo e definir providencia manualmente."


def _format_event(evento: dict[str, Any]) -> str:
    if not evento.get("ha_evento"):
        return "nao confirmado"
    return " ".join(
        part
        for part in [
            str(evento.get("data") or ""),
            str(evento.get("horario_inicio") or ""),
            str(evento.get("local") or ""),
        ]
        if part
    )

def _format_deadline(prazo: dict[str, Any]) -> str:
    if not prazo.get("ha_prazo"):
        return "nao confirmado"
    return " ".join(
        part
        for part in [
            str(prazo.get("data_limite") or ""),
            str(prazo.get("hora_limite") or ""),
            str(prazo.get("risco") or ""),
        ]
        if part
    )
