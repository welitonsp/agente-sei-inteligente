"""Upload local de PDF para o MVP externo/local.

Extrai texto de PDF pesquisavel com `pypdf`, registra apenas hash/metadados e
marca OCR necessario quando nao houver texto extraivel. Nao acessa o SEI real.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any

from app.core import audit
from app.intake.manual_text import (
    ExtractedDeadline,
    ExtractedEvent,
    extract_deadline,
    extract_event,
)
from app.sei.sei_action_guard import GuardRequest, GuardResult, evaluate
from app.storage.db import session_scope
from app.storage.models import Document, Process


MAX_PDF_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class PdfUploadRequest:
    filename: str
    content: bytes
    titulo: str = ""
    processo_sei: str = ""
    origem: str = "web"
    usuario_local: str = ""
    estacao: str = ""


@dataclass(frozen=True)
class PdfUploadResult:
    status: str
    processo_id: int | None
    documento_id: int | None
    file_hash: str
    text_hash: str
    page_count: int
    status_leitura: str
    texto_extraido_caracteres: int
    resumo_executivo: str
    evento: ExtractedEvent
    prazo: ExtractedDeadline
    campos_pendentes: list[str]
    revisao_humana_obrigatoria: bool
    confianca: float
    audit_log_ids: list[int] = field(default_factory=list)
    motivo: str = ""

    def to_contract(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "resultado": {
                "processo_id": self.processo_id,
                "documento_id": self.documento_id,
                "file_hash": self.file_hash,
                "text_hash": self.text_hash,
                "page_count": self.page_count,
                "status_leitura": self.status_leitura,
                "texto_extraido_caracteres": self.texto_extraido_caracteres,
                "resumo_executivo": self.resumo_executivo,
                "evento": self.evento.to_contract(),
                "prazo": self.prazo.to_contract(),
            },
            "confianca": self.confianca,
            "fontes": ["pdf_upload"] if self.file_hash else [],
            "campos_pendentes": self.campos_pendentes,
            "revisao_humana_obrigatoria": self.revisao_humana_obrigatoria,
            "acoes_sugeridas": _suggested_actions(self.evento, self.prazo, self.status_leitura),
            "acoes_bloqueadas": [],
            "logs": self.audit_log_ids,
            "motivo": self.motivo,
        }


def analyze_pdf(request: PdfUploadRequest) -> PdfUploadResult:
    """Analisa PDF enviado pelo usuario, sem persistir texto integral."""
    content = request.content or b""
    file_hash = _hash_bytes(content)
    campos_pendentes = _missing_fields(request)

    if not content:
        audit_id = _record_pdf_log(
            request=request,
            result="precisa_revisao",
            reason="PDF ausente.",
            metadata={"file_hash": file_hash, "status_leitura": "nao_lido"},
        )
        return _result(
            status="precisa_revisao",
            request=request,
            file_hash=file_hash,
            status_leitura="nao_lido",
            campos_pendentes=campos_pendentes,
            audit_log_ids=[audit_id],
            motivo="Arquivo PDF obrigatorio ausente.",
        )

    if len(content) > MAX_PDF_BYTES:
        audit_id = _record_pdf_log(
            request=request,
            result="bloqueado",
            reason="PDF excede o tamanho maximo permitido.",
            metadata={"file_hash": file_hash, "bytes": len(content)},
        )
        return _result(
            status="bloqueado",
            request=request,
            file_hash=file_hash,
            status_leitura="nao_lido",
            campos_pendentes=[*campos_pendentes, "pdf_tamanho"],
            audit_log_ids=[audit_id],
            motivo="PDF excede o tamanho maximo permitido.",
        )

    read_guard = _guard("LER_DOCUMENTO", request)
    audit_ids = [
        audit.record_guard_decision(_guard_request("LER_DOCUMENTO", request), read_guard)
    ]
    if not read_guard.permitido:
        return _result(
            status="bloqueado",
            request=request,
            file_hash=file_hash,
            status_leitura="nao_lido",
            campos_pendentes=campos_pendentes,
            audit_log_ids=audit_ids,
            motivo="Guardiao bloqueou a leitura do PDF.",
        )

    try:
        extracted_text, page_count = extract_pdf_text(content)
    except Exception:
        audit_ids.append(
            _record_pdf_log(
                request=request,
                result="erro",
                reason="Falha ao ler PDF.",
                metadata={"file_hash": file_hash},
            )
        )
        return _result(
            status="erro",
            request=request,
            file_hash=file_hash,
            status_leitura="nao_lido",
            campos_pendentes=[*campos_pendentes, "pdf_invalido"],
            audit_log_ids=audit_ids,
            motivo="Falha ao ler PDF.",
        )

    extracted_text = extracted_text.strip()
    if not extracted_text:
        processo_id, documento_id = _persist_metadata(
            request=request,
            file_hash=file_hash,
            text_hash="",
            summary=_summary_without_text(request, page_count),
            confidence=0.0,
            status_leitura="ocr_necessario",
        )
        audit_ids.append(
            _record_pdf_log(
                request=request,
                result="precisa_revisao",
                reason="PDF sem texto extraivel; OCR necessario.",
                metadata={
                    "documento_id": documento_id,
                    "file_hash": file_hash,
                    "page_count": page_count,
                    "status_leitura": "ocr_necessario",
                },
            )
        )
        return _result(
            status="precisa_revisao",
            request=request,
            processo_id=processo_id,
            documento_id=documento_id,
            file_hash=file_hash,
            page_count=page_count,
            status_leitura="ocr_necessario",
            campos_pendentes=[*campos_pendentes, "ocr_necessario"],
            audit_log_ids=audit_ids,
            resumo=_summary_without_text(request, page_count),
            motivo="PDF sem texto extraivel; OCR necessario.",
        )

    summarize_guard = _guard("RESUMIR", request)
    audit_ids.append(
        audit.record_guard_decision(_guard_request("RESUMIR", request), summarize_guard)
    )
    if not summarize_guard.permitido:
        return _result(
            status="bloqueado",
            request=request,
            file_hash=file_hash,
            status_leitura="lido",
            campos_pendentes=campos_pendentes,
            audit_log_ids=audit_ids,
            motivo="Guardiao bloqueou o resumo do PDF.",
        )

    text_hash = _hash_text(extracted_text)
    evento = extract_event(extracted_text, request.titulo or request.filename)
    prazo = extract_deadline(extracted_text)
    confianca = _confidence(evento, prazo)
    resumo = _summary_with_text(request, extracted_text, page_count, evento, prazo)
    processo_id, documento_id = _persist_metadata(
        request=request,
        file_hash=file_hash,
        text_hash=text_hash,
        summary=resumo,
        confidence=confianca,
        status_leitura="lido",
    )
    audit_ids.append(
        _record_pdf_log(
            request=request,
            result="permitido",
            reason="PDF pesquisavel importado para analise local.",
            metadata={
                "documento_id": documento_id,
                "file_hash": file_hash,
                "text_hash": text_hash,
                "page_count": page_count,
                "texto_extraido_caracteres": len(extracted_text),
                "status_leitura": "lido",
                "evento_detectado": evento.ha_evento,
                "prazo_detectado": prazo.ha_prazo,
            },
        )
    )

    return PdfUploadResult(
        status="precisa_revisao",
        processo_id=processo_id,
        documento_id=documento_id,
        file_hash=file_hash,
        text_hash=text_hash,
        page_count=page_count,
        status_leitura="lido",
        texto_extraido_caracteres=len(extracted_text),
        resumo_executivo=resumo,
        evento=evento,
        prazo=prazo,
        campos_pendentes=campos_pendentes,
        revisao_humana_obrigatoria=True,
        confianca=confianca,
        audit_log_ids=audit_ids,
        motivo="PDF pesquisavel analisado localmente; revisao humana obrigatoria.",
    )


def extract_pdf_text(content: bytes) -> tuple[str, int]:
    """Extrai texto de um PDF pesquisavel e devolve (texto, quantidade_paginas)."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - dependencia declarada
        raise RuntimeError("Leitura de PDF requer pypdf instalado.") from exc

    reader = PdfReader(BytesIO(content))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts), len(reader.pages)


def _persist_metadata(
    *,
    request: PdfUploadRequest,
    file_hash: str,
    text_hash: str,
    summary: str,
    confidence: float,
    status_leitura: str,
) -> tuple[int, int]:
    with session_scope() as session:
        process = Process(
            sei_number=request.processo_sei.strip() or None,
            subject=(request.titulo or request.filename).strip() or None,
            origin=request.origem,
            status="recebida",
        )
        session.add(process)
        session.flush()

        document = Document(
            process_id=process.id,
            source_type="pdf",
            source_reference=request.filename,
            title=(request.titulo or request.filename).strip() or None,
            text_hash=text_hash or file_hash,
            extracted_text_path=None,
            summary=summary,
            classification=f"pdf_{status_leitura}",
            confidence=confidence,
        )
        session.add(document)
        session.flush()
        return process.id, document.id


def _record_pdf_log(
    *,
    request: PdfUploadRequest,
    result: str,
    reason: str,
    metadata: dict[str, Any],
) -> int:
    return audit.record(
        action="LER_DOCUMENTO",
        result=result,
        actor_id=request.usuario_local or None,
        target_type="processo_sei",
        target_id=request.processo_sei or None,
        reason=reason,
        metadata={
            "origem": request.origem,
            "modo_leitura": "pdf_upload",
            "filename": request.filename,
            **metadata,
        },
    )


def _guard(action: str, request: PdfUploadRequest) -> GuardResult:
    return evaluate(_guard_request(action, request))


def _guard_request(action: str, request: PdfUploadRequest) -> GuardRequest:
    return GuardRequest(
        acao_solicitada=action,
        origem="pdf_upload_intake",
        usuario_local=request.usuario_local,
        estacao=request.estacao,
        processo_sei=request.processo_sei,
        justificativa="Upload de PDF no MVP externo/local.",
        aprovado_por_humano=True,
    )


def _result(
    *,
    status: str,
    request: PdfUploadRequest,
    file_hash: str,
    status_leitura: str,
    campos_pendentes: list[str],
    audit_log_ids: list[int],
    motivo: str,
    processo_id: int | None = None,
    documento_id: int | None = None,
    page_count: int = 0,
    resumo: str = "",
) -> PdfUploadResult:
    return PdfUploadResult(
        status=status,
        processo_id=processo_id,
        documento_id=documento_id,
        file_hash=file_hash,
        text_hash="",
        page_count=page_count,
        status_leitura=status_leitura,
        texto_extraido_caracteres=0,
        resumo_executivo=resumo
        or f"PDF '{request.filename or 'sem nome'}' requer revisao humana.",
        evento=ExtractedEvent(),
        prazo=ExtractedDeadline(),
        campos_pendentes=campos_pendentes,
        revisao_humana_obrigatoria=True,
        confianca=0.0,
        audit_log_ids=audit_log_ids,
        motivo=motivo,
    )


def _missing_fields(request: PdfUploadRequest) -> list[str]:
    missing = []
    if not request.content:
        missing.append("pdf")
    if not request.filename.strip():
        missing.append("filename")
    if not request.processo_sei.strip():
        missing.append("processo_sei")
    return missing


def _suggested_actions(
    event: ExtractedEvent, deadline: ExtractedDeadline, status_leitura: str
) -> list[str]:
    actions = []
    if status_leitura == "ocr_necessario":
        actions.append("REVISAR_OCR")
    if event.ha_evento:
        actions.append("REVISAR_EVENTO")
    if deadline.ha_prazo:
        actions.append("REVISAR_PRAZO")
    return actions


def _summary_without_text(request: PdfUploadRequest, page_count: int) -> str:
    return (
        f"PDF '{request.filename or 'sem nome'}' recebido com {page_count} pagina(s), "
        "mas sem texto extraivel. OCR necessario antes de concluir a analise."
    )


def _summary_with_text(
    request: PdfUploadRequest,
    text: str,
    page_count: int,
    event: ExtractedEvent,
    deadline: ExtractedDeadline,
) -> str:
    title = (request.titulo or request.filename or "sem titulo informado").strip()
    parts = [
        f"PDF recebido para analise local: {title}.",
        (
            f"Foram extraidos {len(text)} caracteres de {page_count} pagina(s); "
            "o texto integral nao foi persistido."
        ),
    ]
    if event.ha_evento:
        parts.append(
            f"Possivel evento em {event.data or 'data indefinida'}"
            f"{f' as {event.horario_inicio}' if event.horario_inicio else ''}."
        )
    if deadline.ha_prazo:
        parts.append(f"Possivel prazo administrativo em {deadline.data_limite}.")
    parts.append("Revisao humana obrigatoria antes de qualquer providencia.")
    return " ".join(parts)


def _hash_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest() if content else ""


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _confidence(event: ExtractedEvent, deadline: ExtractedDeadline) -> float:
    return max(0.25, event.confianca, deadline.confianca)
