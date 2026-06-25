"""Cérebro do chat do Agente 19 (lógica pura, testável, sem GUI).

Implementa o fluxo conversacional da FASE 38: o usuário manda o número do
processo e o conteúdo; o agente analisa (tipo, resumo, prazo, providência),
sugere o tipo de documento, gera um rascunho e prepara um resumo para
WhatsApp/Telegram. O agente **nunca** assina, envia ou tramita — e a criação do
documento direto no processo (FASE 5B) permanece gated, fora desta camada.

A leitura automática do processo pela sessão logada é a FRENTE 2 (gated por
`ENABLE_SEI_BROWSER_AUTOMATION`); enquanto não habilitada, o agente pede que o
usuário cole o conteúdo no chat.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

PROCESS_NUMBER_PATTERN = re.compile(r"\b\d{4,}[\d./-]*\d\b")
_MIN_CONTEUDO = 40  # caracteres mínimos para considerar que há conteúdo colado

# Mapeia o tipo provável detectado para um tipo de minuta com template.
_TIPO_MINUTA = {
    "oficio": "oficio",
    "despacho": "despacho",
    "intimacao": "despacho",
    "requisicao": "oficio",
    "informacao": "informacao",
    "encaminhamento": "encaminhamento",
}


@dataclass(frozen=True)
class ChatReply:
    """Uma fala do agente no chat."""

    sender: str  # sempre "agente"
    text: str


def _extrai_processo(mensagem: str) -> str:
    match = PROCESS_NUMBER_PATTERN.search(mensagem)
    return match.group(0) if match else ""


def _conteudo_sem_numero(mensagem: str, processo: str) -> str:
    texto = mensagem.replace(processo, " ") if processo else mensagem
    return " ".join(texto.split())


def _analisar_padrao(texto: str) -> dict[str, Any]:
    from app.intelligence.ai_assist import analise_completa

    return analise_completa(texto)


def _gerar_minuta_padrao(payload: dict[str, Any]) -> dict[str, Any]:
    from app.dashboard.local_app import create_draft_response

    return create_draft_response(payload)


def _fallback_leitura(processo: str, status: str) -> str:
    """Mensagem quando a leitura automática não está disponível."""
    if status == "desabilitado":
        return (
            f"A leitura automática está desligada (Frente 2). Por enquanto, cole "
            f"aqui o texto do processo {processo} que eu analiso."
        )
    if status == "nao_homologado":
        return (
            f"Os seletores de leitura ainda não foram homologados. Cole o texto do "
            f"processo {processo} por enquanto."
        )
    if status == "processo_divergente":
        return (
            f"O processo aberto no SEI não confere com {processo}. Abra esse "
            f"processo no SEI e tente de novo, ou cole o texto aqui."
        )
    return (
        f"Não consegui ler o processo {processo} automaticamente. Pode colar o "
        f"texto aqui que eu analiso."
    )


def telegram_summary(analise: dict[str, Any], processo: str) -> str:
    """Monta um resumo curto e sanitizado para WhatsApp/Telegram."""
    tipo = analise.get("tipo_provavel", "indefinido")
    resumo = analise.get("resumo_curto", "")
    providencia = analise.get("providencia_sugerida", "")
    prazos = analise.get("prazos", []) or []
    if prazos:
        p = prazos[0]
        limite = f" (até {p['data_limite']})" if p.get("data_limite") else ""
        prazo_txt = f"{p.get('descricao', '')}{limite}"
    else:
        prazo_txt = "não identificado"
    linhas = [
        f"Agente 19 - Processo {processo or 'sem numero'}",
        f"Tipo: {tipo}",
        f"Resumo: {resumo}",
        f"Prazo: {prazo_txt}",
        f"Providencia: {providencia}",
        "Rascunho pronto para revisao. O agente nao assina nem envia.",
    ]
    return "\n".join(linhas)


class AgentChatController:
    """Conduz a conversa do Agente 19 sem tocar em GUI."""

    def __init__(
        self,
        *,
        analisar: Callable[[str], dict[str, Any]] | None = None,
        gerar_minuta: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
        ler_processo: Callable[[str], Any] | None = None,
    ) -> None:
        self._analisar = analisar or _analisar_padrao
        self._gerar = gerar_minuta or _gerar_minuta_padrao
        # Leitura automática (Frente 2): opcional e gated. Quando ausente ou
        # indisponível, o chat pede o texto colado (comportamento atual).
        self._ler_processo = ler_processo

    def saudacao(self) -> ChatReply:
        return ChatReply(
            "agente",
            "Sou o Agente 19. Me passe o número do processo SEI e cole o texto do "
            "documento que você quer analisar. Vou identificar o tipo, resumir, "
            "achar prazos e sugerir um rascunho. Não assino nem envio nada.",
        )

    def responder(self, mensagem: str) -> list[ChatReply]:
        mensagem = (mensagem or "").strip()
        if not mensagem:
            return [ChatReply("agente", "Não recebi nada. Envie o número do processo e o conteúdo.")]

        processo = _extrai_processo(mensagem)
        conteudo = _conteudo_sem_numero(mensagem, processo)

        if not processo and len(conteudo) < _MIN_CONTEUDO:
            return [ChatReply("agente", "Qual é o número do processo SEI?")]

        if len(conteudo) < _MIN_CONTEUDO:
            return self._ler_ou_pedir_texto(processo)

        return self._analisar_e_sugerir(processo, conteudo)

    def _ler_ou_pedir_texto(self, processo: str) -> list[ChatReply]:
        """Tenta a leitura automática (gated); senão, pede o texto colado."""
        if self._ler_processo is not None:
            resultado = self._ler_processo(processo)
            status = getattr(resultado, "status", "erro")
            if status == "ok":
                texto = getattr(resultado, "texto", "")
                intro = ChatReply(
                    "agente",
                    f"Li o processo {processo} pela sua sessão (somente leitura).",
                )
                return [intro] + self._analisar_e_sugerir(processo, texto)
            return [ChatReply("agente", _fallback_leitura(processo, status))]

        return [
            ChatReply(
                "agente",
                f"Recebi o processo {processo}. Por enquanto, cole aqui o texto do "
                "documento — a leitura automática pela sua sessão logada é a "
                "próxima fase. Quando você colar, eu analiso.",
            )
        ]

    def _analisar_e_sugerir(self, processo: str, conteudo: str) -> list[ChatReply]:
        analise = self._analisar(conteudo)
        tipo = analise.get("tipo_provavel", "indefinido")
        resumo = analise.get("resumo_curto", "")
        providencia = analise.get("providencia_sugerida", "")
        prazos = analise.get("prazos", []) or []

        replies = [
            ChatReply("agente", f"Analisei o processo {processo}. Tipo provável: {tipo}."),
            ChatReply("agente", f"Resumo: {resumo}"),
        ]
        if prazos:
            p = prazos[0]
            limite = f", data-limite {p['data_limite']}" if p.get("data_limite") else ""
            replies.append(
                ChatReply("agente", f"Prazo identificado: {p.get('descricao', '')}{limite}.")
            )
        else:
            replies.append(ChatReply("agente", "Não identifiquei prazo explícito."))
        replies.append(ChatReply("agente", f"Providência sugerida: {providencia}"))

        tipo_minuta = _TIPO_MINUTA.get(tipo, "despacho")
        rascunho = self._rascunho(processo, tipo_minuta, resumo)
        replies.append(
            ChatReply("agente", f"Sugiro criar um {tipo_minuta}. Rascunho para revisão:\n{rascunho}")
        )
        replies.append(
            ChatReply("agente", "Resumo para WhatsApp/Telegram:\n" + telegram_summary(analise, processo))
        )
        replies.append(
            ChatReply(
                "agente",
                "O rascunho está pronto para você copiar no SEI. Eu NÃO assino nem "
                "envio. Criar o documento direto no processo é uma fase seguinte, que "
                "depende da sua autorização expressa.",
            )
        )
        return replies

    def _rascunho(self, processo: str, tipo_minuta: str, resumo: str) -> str:
        try:
            contrato = self._gerar(
                {
                    "assunto": f"Processo {processo}",
                    "resumo": resumo,
                    "tipo_minuta": tipo_minuta,
                    "processo_sei": processo,
                    "origem": "chat_flutuante",
                }
            )
        except Exception:
            return "(não foi possível gerar o rascunho automaticamente — revise manualmente)"
        resultado = contrato.get("resultado", {}) if isinstance(contrato, dict) else {}
        return str(resultado.get("texto", "")).strip() or "(rascunho vazio)"
