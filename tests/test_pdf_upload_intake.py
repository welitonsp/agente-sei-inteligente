"""Testes do upload local de PDF."""

from __future__ import annotations

import base64
from io import BytesIO

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.dashboard.local_app import create_import_pdf_response
from app.intake.pdf_upload import PdfUploadRequest, analyze_pdf, extract_pdf_text


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    import app.storage.db as db
    import app.storage.models as models

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'pdf_upload.db').as_posix()}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    db.Base.metadata.create_all(engine)
    monkeypatch.setattr(
        db,
        "SessionLocal",
        sessionmaker(bind=engine, autoflush=False, expire_on_commit=False),
    )
    return db, models


def _pdf_with_text(text: str) -> bytes:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n"
        + stream
        + b"\nendstream",
    ]
    chunks = [b"%PDF-1.4\n"]
    offsets = [0]
    current = len(chunks[0])
    for index, obj in enumerate(objects, start=1):
        offsets.append(current)
        chunk = f"{index} 0 obj\n".encode("ascii") + obj + b"\nendobj\n"
        chunks.append(chunk)
        current += len(chunk)
    xref_offset = current
    xref = [b"xref\n", b"0 6\n", b"0000000000 65535 f \n"]
    for offset in offsets[1:]:
        xref.append(f"{offset:010d} 00000 n \n".encode("ascii"))
    trailer = (
        b"trailer\n<< /Root 1 0 R /Size 6 >>\nstartxref\n"
        + str(xref_offset).encode("ascii")
        + b"\n%%EOF\n"
    )
    return b"".join([*chunks, *xref, trailer])


def _blank_pdf() -> bytes:
    from pypdf import PdfWriter

    buffer = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(buffer)
    return buffer.getvalue()


def test_extract_pdf_text_pesquisavel():
    text, pages = extract_pdf_text(_pdf_with_text("Prazo ate 2026-07-02."))

    assert pages == 1
    assert "Prazo ate 2026-07-02" in text


def test_pdf_pesquisavel_persiste_metadados_sem_texto_integral(db_env):
    db, models = db_env
    marcador = "NAO_PERSISTIR_TEXTO_COMPLETO"
    pdf = _pdf_with_text(
        f"Convocacao para reuniao em 2026-07-01 as 09:00. Local: 19 CRPM. {marcador}"
    )

    result = analyze_pdf(
        PdfUploadRequest(
            filename="convocacao.pdf",
            content=pdf,
            titulo="Convocacao",
            processo_sei="2026.000129",
            usuario_local="operador.local",
        )
    )

    assert result.status == "precisa_revisao"
    assert result.status_leitura == "lido"
    assert result.page_count == 1
    assert result.evento.ha_evento is True
    assert result.text_hash
    assert marcador not in result.resumo_executivo

    with db.session_scope() as session:
        document = session.get(models.Document, result.documento_id)
        assert document.source_type == "pdf"
        assert document.source_reference == "convocacao.pdf"
        assert document.extracted_text_path is None
        assert document.classification == "pdf_lido"
        assert marcador not in (document.summary or "")

        logs = session.query(models.AuditLog).all()
        for row in logs:
            blob = f"{row.reason} {row.meta_json}"
            assert marcador not in blob
            assert "texto" not in (row.meta_json or {})


def test_pdf_sem_texto_marca_ocr_necessario(db_env):
    db, models = db_env

    result = analyze_pdf(
        PdfUploadRequest(
            filename="imagem.pdf",
            content=_blank_pdf(),
            titulo="PDF digitalizado",
            processo_sei="2026.000130",
        )
    )

    assert result.status == "precisa_revisao"
    assert result.status_leitura == "ocr_necessario"
    assert "ocr_necessario" in result.campos_pendentes
    assert result.documento_id is not None

    with db.session_scope() as session:
        document = session.get(models.Document, result.documento_id)
        assert document.classification == "pdf_ocr_necessario"


def test_pdf_invalido_nao_cria_documento(db_env):
    db, models = db_env

    result = analyze_pdf(
        PdfUploadRequest(
            filename="quebrado.pdf",
            content=b"isto nao e pdf",
            processo_sei="2026.000131",
        )
    )

    assert result.status == "erro"
    assert "pdf_invalido" in result.campos_pendentes
    with db.session_scope() as session:
        assert session.query(models.Document).count() == 0
        assert session.query(models.Process).count() == 0


def test_dashboard_import_pdf_response(db_env):
    pdf = _pdf_with_text("Prazo urgente para responder ate 02/07/2026 as 17h30.")

    response = create_import_pdf_response(
        {
            "filename": "prazo.pdf",
            "content_base64": base64.b64encode(pdf).decode("ascii"),
            "titulo": "Prazo administrativo",
            "processo_sei": "2026.000132",
        }
    )

    assert response["status"] == "precisa_revisao"
    assert response["resultado"]["status_leitura"] == "lido"
    assert response["resultado"]["prazo"]["ha_prazo"] is True
    assert response["resultado"]["prazo"]["data_limite"] == "2026-07-02"
