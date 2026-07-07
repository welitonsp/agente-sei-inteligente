"""Testes da integração da IA ao pipeline de análise (com gate de dados)."""

from __future__ import annotations

from app.core.config import Settings
from app.intelligence.ai_assist import analise_completa, resumo_assistido
from app.intelligence.ai_provider import AICompletion, EchoProvider


class _ProvedorRealFake:
    """Simula um provedor externo (is_real=True) com saída controlada."""

    is_real = True

    def __init__(self) -> None:
        self.chamado = False

    def complete(self, role, prompt, *, system=None):
        self.chamado = True
        return AICompletion(text="Resumo do Claude.", role=role, model="claude-opus-4-8")


class _ProvedorQueFalha:
    is_real = True

    def complete(self, role, prompt, *, system=None):
        raise RuntimeError("sem credencial")


def test_echo_usa_caminho_ia_offline():
    # Echo não é externo: não é gated pela flag; produz resultado via provedor.
    r = resumo_assistido("Ofício para resposta.", provider=EchoProvider(),
                         settings=Settings())
    assert r.fonte == "ia"
    assert r.modelo == "echo"


def test_ia_externa_bloqueada_por_padrao_usa_local():
    prov = _ProvedorRealFake()
    settings = Settings(sei_allow_external_ai_for_live_content=False)
    r = resumo_assistido("Despacho para análise no prazo de 5 dias.",
                         provider=prov, settings=settings)
    assert r.fonte == "local"
    assert r.motivo == "ia_externa_desabilitada"
    assert prov.chamado is False  # não enviou conteúdo externamente


def test_ia_externa_liberada_usa_provedor():
    prov = _ProvedorRealFake()
    settings = Settings(sei_allow_external_ai_for_live_content=True)
    r = resumo_assistido("Ofício.", provider=prov, settings=settings)
    assert r.fonte == "ia"
    assert r.modelo == "claude-opus-4-8"
    assert prov.chamado is True


def test_falha_de_ia_degrada_para_local():
    settings = Settings(sei_allow_external_ai_for_live_content=True)
    r = resumo_assistido("Intimação.", provider=_ProvedorQueFalha(), settings=settings)
    assert r.fonte == "local"
    assert r.motivo.startswith("falha_ia:")


def test_resumo_assistido_sanitiza_pii_da_ia():
    class _ProvVazaPII:
        is_real = True

        def complete(self, role, prompt, *, system=None):
            return AICompletion(text="Intimar CPF 123.456.789-00.", role=role, model="m")

    settings = Settings(sei_allow_external_ai_for_live_content=True)
    r = resumo_assistido("x", provider=_ProvVazaPII(), settings=settings)
    assert "123.456.789-00" not in r.texto
    assert "123.***.***-00" in r.texto


def test_analise_completa_mantem_chaves_e_anexa_proveniencia():
    settings = Settings(sei_allow_external_ai_for_live_content=False)
    out = analise_completa(
        "Ofício: responder no prazo de 5 dias.",
        provider=EchoProvider(),
        settings=settings,
    )
    # Mantém o contrato da análise local...
    assert out["tipo_provavel"] == "oficio"
    assert out["prazo_detectado"] is True
    # ...e anexa a proveniência do resumo.
    assert out["resumo_fonte"] in {"ia", "local"}
    assert "resumo_modelo" in out
