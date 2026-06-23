"""Testes do minutador local zero custo."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.intelligence.local_minutador import DraftRequest, generate_draft, infer_draft_type


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    import app.storage.db as db
    import app.storage.models as models

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'minutador.db').as_posix()}",
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


def test_infer_draft_type_por_regras():
    assert infer_draft_type("Elaborar oficio de resposta externa") == "oficio"
    assert infer_draft_type("Prestar informacao administrativa") == "informacao"
    assert infer_draft_type("Encaminhar para providencias") == "encaminhamento"
    assert infer_draft_type("Ha prazo para providencia nos autos") == "despacho"


@pytest.mark.parametrize(
    ("tipo", "cabecalho"),
    [
        ("despacho", "DESPACHO"),
        ("oficio", "OFICIO"),
        ("informacao", "INFORMACAO"),
        ("encaminhamento", "ENCAMINHAMENTO"),
    ],
)
def test_generate_draft_tipos_locais(db_env, tipo, cabecalho):
    result = generate_draft(
        DraftRequest(
            tipo_minuta=tipo,
            assunto="Apoio administrativo",
            resumo="solicitacao de apoio para atividade institucional",
            processo_sei="2026.000200",
            unidade_destino="PM/19 CRPM",
            destinatario="Comando da Unidade",
            usuario_local="operador.local",
        )
    )

    contract = result.to_contract()

    assert result.status == "precisa_revisao"
    assert result.revisao_humana_obrigatoria is True
    assert result.tipo_minuta == tipo
    assert cabecalho in result.texto
    assert "2026.000200" in result.texto
    assert "ASSINAR_DOCUMENTO" in contract["acoes_bloqueadas"]
    assert "TRAMITAR_PROCESSO" in contract["acoes_bloqueadas"]
    assert contract["fontes"] == ["template_local", "regras_locais"]


def test_generate_draft_mantem_placeholders_quando_falta_dado(db_env):
    result = generate_draft(
        DraftRequest(
            assunto="",
            resumo="pedido de providencia",
            processo_sei="",
            tipo_minuta="despacho",
        )
    )

    assert "[PREENCHER assunto]" in result.texto
    assert "[PREENCHER processo SEI]" in result.texto
    assert "unidade_destino" in result.campos_pendentes
    assert result.confianca < 0.7


def test_auditoria_nao_grava_texto_base_integral(db_env):
    db, models = db_env
    marcador = "TRECHO_COMPLETO_NAO_DEVE_IR_PARA_AUDITORIA"

    result = generate_draft(
        DraftRequest(
            assunto="Encaminhamento",
            texto_base=f"Encaminhar para providencias. {marcador}",
            processo_sei="2026.000201",
            unidade_destino="PM/19 CRPM",
            usuario_local="operador.local",
        )
    )

    assert result.audit_log_ids
    with db.session_scope() as session:
        logs = session.query(models.AuditLog).all()
        assert len(logs) == len(result.audit_log_ids)
        for row in logs:
            blob = f"{row.reason} {row.meta_json}"
            assert marcador not in blob
            assert "texto_base" not in (row.meta_json or {})

