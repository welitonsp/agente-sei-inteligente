"""Garante que segredos nunca sao persistidos em log ou auditoria."""

from app.core.security_filter import REDACTED, contains_secret_key, sanitize


def test_sanitiza_senha_e_token_no_topo():
    dados = {"usuario": "joao", "senha_sei": "1234", "token": "abc"}
    limpo = sanitize(dados)
    assert limpo["usuario"] == "joao"
    assert limpo["senha_sei"] == REDACTED
    assert limpo["token"] == REDACTED


def test_sanitiza_em_profundidade():
    dados = {
        "ctx": {"cookie_sei": "x", "processo": "123"},
        "lista": [{"authorization": "Bearer y"}, {"ok": 1}],
    }
    limpo = sanitize(dados)
    assert limpo["ctx"]["cookie_sei"] == REDACTED
    assert limpo["ctx"]["processo"] == "123"
    assert limpo["lista"][0]["authorization"] == REDACTED
    assert limpo["lista"][1]["ok"] == 1


def test_detecta_presenca_de_segredo():
    assert contains_secret_key({"refresh_token": "x"}) is True
    assert contains_secret_key({"ctx": {"client_secret": "y"}}) is True
    assert contains_secret_key({"processo": "123", "assunto": "reuniao"}) is False


def test_nao_altera_dados_sem_segredo():
    dados = {"processo": "123", "assunto": "reuniao", "itens": [1, 2, 3]}
    assert sanitize(dados) == dados
