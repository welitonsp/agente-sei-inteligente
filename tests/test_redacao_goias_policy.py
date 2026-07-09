"""Testes da policy deterministica do Manual de Redacao de Goias (FASE 65)."""

from __future__ import annotations

from app.intelligence.redacao_goias_policy import ChecklistItem, evaluate_redacao


def _item(verdict, item_id: str) -> ChecklistItem:
    return next(i for i in verdict.checklist if i.id == item_id)


# --- caminho feliz -----------------------------------------------------------


DESPACHO_OK = (
    "DESPACHO\n\n"
    "Processo SEI: 202600000000000\n"
    "Assunto: apoio operacional\n\n"
    "Considerando o teor da demanda, encaminhe-se a PM/19 CRPM para "
    "conhecimento e adocao das providencias cabiveis.\n"
)


def test_despacho_bem_formado_aprova():
    v = evaluate_redacao(DESPACHO_OK, tipo_minuta="despacho")
    assert v.ok is True
    assert v.bloqueado is False
    assert v.score >= 0.9
    assert v.pendencias == []


# --- bloqueantes -------------------------------------------------------------


def test_promessa_de_ato_proibido_bloqueia():
    texto = DESPACHO_OK + "\nAssino e tramito o processo em seguida."
    v = evaluate_redacao(texto, tipo_minuta="despacho")
    assert v.bloqueado is True
    assert v.ok is False
    assert not _item(v, "sem_promessa_ato").ok
    assert any("ato proibido" in b.lower() for b in v.bloqueios)


def test_assinatura_simulada_bloqueia():
    texto = DESPACHO_OK + "\nDocumento assinado eletronicamente por Fulano."
    v = evaluate_redacao(texto, tipo_minuta="despacho")
    assert v.bloqueado is True
    assert not _item(v, "sem_assinatura_simulada").ok


def test_dado_sensivel_bloqueia():
    texto = DESPACHO_OK + "\nA senha do sistema e 1234."
    v = evaluate_redacao(texto, tipo_minuta="despacho")
    assert v.bloqueado is True
    assert not _item(v, "sem_dado_sensivel").ok


# --- pendencias (nao bloqueiam, mas ok=False) --------------------------------


def test_oficio_sem_fecho_e_tratamento_gera_pendencia():
    texto = (
        "OFICIO\n\nProcesso SEI: 202600000000000\nAssunto: resposta\n\n"
        "Em atencao ao expediente, informo o andamento.\n"
    )
    v = evaluate_redacao(texto, tipo_minuta="oficio")
    assert v.bloqueado is False  # nao e bloqueante
    assert v.ok is False  # mas ha pendencia
    assert not _item(v, "fecho_adequado").ok
    assert not _item(v, "forma_tratamento").ok


def test_impessoalidade_quebrada_gera_pendencia():
    texto = DESPACHO_OK + "\nEu acredito que meu parecer resolve a questao."
    v = evaluate_redacao(texto, tipo_minuta="despacho")
    assert not _item(v, "impessoalidade").ok
    assert v.bloqueado is False


def test_placeholder_e_pendencia_nao_bloqueio():
    texto = DESPACHO_OK.replace("PM/19 CRPM", "[PREENCHER unidade]")
    v = evaluate_redacao(texto, tipo_minuta="despacho")
    assert v.bloqueado is False
    assert not _item(v, "campos_pendentes_marcados").ok
    assert any("preencher" in p.lower() for p in v.pendencias)


def test_estrutura_incompleta_para_tipo():
    v = evaluate_redacao("Texto solto sem cabecalho.", tipo_minuta="portaria")
    assert not _item(v, "estrutura_completa").ok
    detalhe = _item(v, "estrutura_completa").detalhe
    assert "portaria" in detalhe or "resolve" in detalhe


# --- contrato + robustez -----------------------------------------------------


def test_contract_tem_formato_docs65():
    v = evaluate_redacao(DESPACHO_OK, tipo_minuta="despacho")
    contrato = v.to_contract()
    assert contrato["revisao_humana_obrigatoria"] is True
    assert "checklist" in contrato
    assert isinstance(contrato["pendencias"], list)


def test_tipo_desconhecido_nao_quebra():
    v = evaluate_redacao(DESPACHO_OK, tipo_minuta="")
    assert isinstance(v.score, float)
    # Sem tipo, nao exige estrutura especifica nem fecho.
    assert _item(v, "estrutura_completa").ok
