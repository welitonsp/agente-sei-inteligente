"""Testes do painel MVP local."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.dashboard import local_app


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    import app.storage.db as db
    import app.storage.models as models

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'dashboard.db').as_posix()}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    db.Base.metadata.create_all(engine)
    monkeypatch.setattr(
        db,
        "SessionLocal",
        sessionmaker(bind=engine, autoflush=False, expire_on_commit=False),
    )
    
    def mock_analyze(request):
        from app.intake.manual_text import ManualTextResult, ExtractedEvent, ExtractedDeadline
        import hashlib
        text_hash = hashlib.sha256(request.texto.encode("utf-8")).hexdigest()
        return ManualTextResult(
            status="precisa_revisao",
            processo_id=None,
            documento_id=None,
            text_hash=text_hash,
            resumo_executivo="Resumo mockado seguro",
            evento=ExtractedEvent(ha_evento=True),
            prazo=ExtractedDeadline(ha_prazo=False),
            campos_pendentes=[],
            revisao_humana_obrigatoria=True,
            confianca=0.99,
            audit_log_ids=[],
            motivo="Mock",
        )
    
    # Mocking as funcoes internas utilizadas pelo grafo
    monkeypatch.setattr("app.dashboard.local_app.analyze_text", mock_analyze)
    monkeypatch.setattr("app.intelligence.graph.nodes.analyze_with_gemini", mock_analyze)
    monkeypatch.setattr("app.intelligence.graph.nodes.review_with_gemini", lambda *a, **k: {"aprovado": True, "feedback": ""})

    return db, models


def test_index_tem_campos_minimos_do_checklist():
    html = local_app.INDEX_HTML

    assert 'name="processo_sei"' in html
    assert 'name="texto"' in html
    assert 'name="pdf"' in html
    assert 'name="perfil_local"' in html
    assert "Analisar para o 19 CRPM" in html
    assert "Revisao humana" in html
    assert "Campos pendentes" in html
    assert "/api/import-pdf" in html
    assert "/api/generate-draft" in html
    assert "/api/triage-local" in html
    assert "/api/mission-control" in html
    assert "Gerar minuta local" in html
    assert "Triagem local" in html
    assert "Missao Agente 19" in html


def test_create_import_text_response_retorna_resultado_estruturado(db_env):
    db, models = db_env

    response = local_app.create_import_text_response(
        {
            "titulo": "Reuniao operacional",
            "texto": "Convocacao para reuniao em 2026-07-01 as 09:00. Local: 19 CRPM.",
            "processo_sei": "2026.000126",
            "usuario_local": "operador.local",
        }
    )

    assert response["status"] == "pronto_para_revisao" or response["status"] == "precisa_revisao"
    assert response["revisao_humana_obrigatoria"] is True
    assert response["resultado"]["evento"]["ha_evento"] is True
    assert response["resultado"]["text_hash"]


def test_create_import_text_response_nao_retorna_texto_integral(db_env):
    marcador = "NAO_RETORNAR_ESTE_TEXTO"

    response = local_app.create_import_text_response(
        {
            "titulo": "Prazo",
            "texto": f"Prazo ate 2026-07-02. {marcador}",
            "processo_sei": "2026.000127",
        }
    )

    blob = str(response)
    assert marcador not in blob
    assert response["resultado"]["text_hash"]


def test_create_draft_response_gera_minuta_local(db_env):
    db, models = db_env

    response = local_app.create_draft_response(
        {
            "assunto": "Apoio administrativo",
            "resumo": "pedido de apoio para atividade institucional",
            "processo_sei": "2026.000300",
            "tipo_minuta": "despacho",
            "unidade_destino": "PM/19 CRPM",
            "usuario_local": "operador.local",
        }
    )

    assert response["status"] == "precisa_revisao"
    assert response["revisao_humana_obrigatoria"] is True
    assert response["resultado"]["tipo_minuta"] == "despacho"
    assert "DESPACHO" in response["resultado"]["texto"]
    assert "ASSINAR_DOCUMENTO" in response["acoes_bloqueadas"]

    with db.session_scope() as session:
        assert session.query(models.AuditLog).count() >= 1


def test_create_triage_response_sem_regras_nao_inventa_unidade(db_env):
    response = local_app.create_triage_response(
        {
            "assunto": "Apoio administrativo",
            "texto": "Solicitacao de apoio administrativo.",
            "processo_sei": "2026.000301",
        }
    )

    assert response["status"] == "precisa_revisao"
    assert response["resultado"]["interesse_19crpm"] == "indefinido"
    assert response["resultado"]["unidade_sugerida"] == ""
    assert response["revisao_humana_obrigatoria"] is True
    assert "DECIDIR_UNIDADE_SEM_REGRA" in response["acoes_bloqueadas"]


def test_create_mission_response_orquestra_fluxo_supervisionado(db_env):
    response = local_app.create_mission_response(
        {
            "titulo": "Oficio de apoio",
            "texto": "Oficio solicitando apoio do 19 CRPM no prazo de 10 dias uteis.",
            "processo_sei": "2026.000400",
            "unidade_destino": "PM/19 CRPM",
            "tipo_minuta": "despacho",
            "usuario_local": "operador.local",
        }
    )

    assert response["status"] == "pronto_para_revisao"
    assert response["revisao_humana_obrigatoria"] is True
    assert response["resultado"]["plano_operacional"]
    assert response["resultado"]["minuta"]["texto"]
    assert "ASSINAR_DOCUMENTO" in response["acoes_bloqueadas"]


def test_create_agent19_response_expoe_nucleo_de_agente(db_env):
    response = local_app.create_agent19_response(
        {
            "mensagem": "Analise o processo para o 19 CRPM.",
            "titulo": "Oficio de apoio",
            "texto": "Oficio solicitando apoio do 19 CRPM no prazo de 10 dias uteis.",
            "processo_sei": "2026.000800",
            "usuario_local": "operador.local",
            "perfil_local": "operador",
        }
    )

    assert response["agente"]["nome"] == "Agente 19"
    assert response["agente"]["tipo"] == "servidor_digital_ia_supervisionado"
    assert response["ferramentas_usadas"][0]["ferramenta"] == "mission_control"
    assert response["revisao_humana_obrigatoria"] is True
