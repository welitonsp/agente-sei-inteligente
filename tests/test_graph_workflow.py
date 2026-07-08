"""Testes do grafo cognitivo LangGraph e da camada de raciocinio de IA.

Cobrem o subsistema que antes nao tinha testes: roteamento pelo provedor sob
guarda, critico FAIL-CLOSED, loop de auto-correcao e persistencia de auditoria.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.intelligence.ai_provider import AICompletion, AIRole
from app.intelligence.ai_reasoning import ReviewVerdict, review_minuta, summarize_process


# --- Fakes -------------------------------------------------------------------


class _FakeProvider:
    """Provedor 'real' controlavel: devolve um texto fixo por chamada."""

    is_real = True

    def __init__(self, text: str) -> None:
        self._text = text
        self.roles: list[AIRole] = []

    def complete(self, role, prompt, *, system=None):
        self.roles.append(role)
        return AICompletion(text=self._text, role=role, model="fake")


class _BoomProvider:
    is_real = True

    def complete(self, role, prompt, *, system=None):
        raise RuntimeError("rede caiu")


@pytest.fixture()
def echo_env(monkeypatch):
    """Forca o provedor offline deterministico (EchoProvider) no processo."""
    monkeypatch.setenv("AI_PROVIDER", "echo")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    import app.storage.db as db

    engine = create_engine(
        f"sqlite:///{(tmp_path / 'graph.db').as_posix()}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    db.Base.metadata.create_all(engine)
    monkeypatch.setattr(
        db,
        "SessionLocal",
        sessionmaker(bind=engine, autoflush=False, expire_on_commit=False),
    )
    return db


# --- Camada de raciocinio ----------------------------------------------------


def test_summarize_usa_papel_resumo(echo_env):
    provider = _FakeProvider("resumo fiel do processo")
    out = summarize_process("Titulo", "Corpo do processo", provider=provider)
    assert out == "resumo fiel do processo"
    assert provider.roles == [AIRole.RESUMO]


def test_review_parseia_json_aprovado():
    provider = _FakeProvider('{"aprovado": true, "feedback": "OK"}')
    v = review_minuta("base", "minuta", "ctx", provider=provider)
    assert v.disponivel is True
    assert v.aprovado is True


def test_review_parseia_json_reprovado_com_ruido():
    provider = _FakeProvider('Claro:\n{"aprovado": false, "feedback": "inventou prazo"}\nfim')
    v = review_minuta("base", "minuta", "ctx", provider=provider)
    assert v.disponivel is True
    assert v.aprovado is False
    assert "prazo" in v.feedback


def test_review_fail_closed_quando_offline(echo_env):
    """EchoProvider (is_real=False) NUNCA aprova sozinho."""
    v = review_minuta("base", "minuta", "ctx")
    assert v.disponivel is False
    assert v.aprovado is False


def test_review_fail_closed_quando_erro():
    v = review_minuta("base", "minuta", "ctx", provider=_BoomProvider())
    assert v.disponivel is False
    assert v.aprovado is False
    assert "falhou" in v.feedback.lower()


def test_review_fail_closed_quando_json_invalido():
    provider = _FakeProvider("APROVADO sem json nenhum")
    v = review_minuta("base", "minuta", "ctx", provider=provider)
    assert v.disponivel is False
    assert v.aprovado is False


# --- Grafo -------------------------------------------------------------------


def test_checklist_para_quando_falta_campo(echo_env):
    from app.intelligence.graph.workflow import create_agent_graph

    app = create_agent_graph()
    final = app.invoke(
        {
            "processo_sei": "",  # faltando -> precisa_complemento -> END
            "titulo": "Assunto qualquer",
            "texto_original": "Corpo do processo para analise.",
            "usuario_local": "tester",
            "unidade_destino": "",
            "tipo_minuta": "",
            "resumo": "",
            "campos_pendentes": [],
            "minuta_texto": "",
            "alertas": [],
            "confianca": 0.5,
            "revisao_humana_obrigatoria": True,
            "status": "iniciado",
            "tentativas_critica": 0,
        }
    )
    assert final["status"] == "precisa_complemento"
    assert "processo_sei" in final["campos_pendentes"]
    assert not final["minuta_texto"]  # nao gerou minuta


def test_fluxo_completo_gera_minuta_e_audita(echo_env, db_env):
    from app.intelligence.graph.workflow import create_agent_graph

    app = create_agent_graph()
    final = app.invoke(
        {
            "processo_sei": "2024.001",
            "titulo": "Encaminhamento de oficio",
            "texto_original": "Encaminhar oficio ao setor responsavel.",
            "usuario_local": "tester",
            "unidade_destino": "PM/19 CRPM",
            "tipo_minuta": "despacho",
            "resumo": "",
            "campos_pendentes": [],
            "minuta_texto": "",
            "alertas": [],
            "confianca": 0.5,
            "revisao_humana_obrigatoria": True,
            "status": "iniciado",
            "tentativas_critica": 0,
        }
    )
    # Offline: critico e fail-closed -> pronto para revisao humana, minuta gerada.
    assert final["status"] == "pronto_para_revisao"
    assert final["minuta_texto"]
    assert final["revisao_humana_obrigatoria"] is True
    # Auditoria automatica indisponivel offline deve estar sinalizada.
    assert any("auditoria automatica" in a.lower() for a in final["alertas"])
    # E o audit_node deve ter persistido um registro (id na mensagem final).
    assert any("Auditoria registrada" in a for a in final["alertas"])


def test_loop_de_autocorrecao_reprova_e_reescreve(echo_env, db_env, monkeypatch):
    """Critico reprovando 2x deve reentrar em draft e convergir em <=3 tentativas."""
    from app.intelligence.graph import nodes

    chamadas = {"n": 0}

    def fake_review(*args, **kwargs):
        chamadas["n"] += 1
        if chamadas["n"] < 2:
            return ReviewVerdict(disponivel=True, aprovado=False, feedback="ajustar tom")
        return ReviewVerdict(disponivel=True, aprovado=True, feedback="")

    monkeypatch.setattr(nodes, "review_minuta", fake_review)

    from app.intelligence.graph.workflow import create_agent_graph

    app = create_agent_graph()
    final = app.invoke(
        {
            "processo_sei": "2024.002",
            "titulo": "Informacao ao comando",
            "texto_original": "Prestar informacao sobre a demanda.",
            "usuario_local": "tester",
            "unidade_destino": "PM/19 CRPM",
            "tipo_minuta": "informacao",
            "resumo": "",
            "campos_pendentes": [],
            "minuta_texto": "",
            "alertas": [],
            "confianca": 0.5,
            "revisao_humana_obrigatoria": True,
            "status": "iniciado",
            "tentativas_critica": 0,
        }
    )
    assert chamadas["n"] >= 2  # reprovou e reavaliou
    assert final["status"] == "pronto_para_revisao"
    assert final["tentativas_critica"] >= 2
