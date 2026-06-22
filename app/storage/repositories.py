import json
from typing import Dict, Any, List
from app.storage.database import get_connection

def add_unidade_pmgo(sigla: str, nome: str, tipo_unidade: str, municipio: str, email_institucional: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO unidades_pmgo (sigla, nome, tipo_unidade, municipio, email_institucional) VALUES (?, ?, ?, ?, ?)",
            (sigla, nome, tipo_unidade, municipio, email_institucional)
        )

def list_unidades_pmgo() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM unidades_pmgo")
        return [dict(row) for row in cursor.fetchall()]

def add_modelo_aprovado(tipo_documento: str, titulo: str, conteudo_template: str, origem: str, aprovado_por: str, versao: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO modelos_aprovados (tipo_documento, titulo, conteudo_template, origem, aprovado_por, versao) VALUES (?, ?, ?, ?, ?, ?)",
            (tipo_documento, titulo, conteudo_template, origem, aprovado_por, versao)
        )

def list_modelos_aprovados() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM modelos_aprovados")
        return [dict(row) for row in cursor.fetchall()]

def add_correcao_usuario(tipo_documento: str, texto_original_hash: str, texto_corrigido_hash: str, resumo_correcao: str, aprovado_por: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO correcoes_usuario (tipo_documento, texto_original_hash, texto_corrigido_hash, resumo_correcao, aprovado_por) VALUES (?, ?, ?, ?, ?)",
            (tipo_documento, texto_original_hash, texto_corrigido_hash, resumo_correcao, aprovado_por)
        )

def list_correcoes_usuario() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM correcoes_usuario")
        return [dict(row) for row in cursor.fetchall()]

def add_decisao_validada(tipo_processo: str, assunto_detectado: str, documento_escolhido: str, providencia_aprovada: str, confianca: float, aprovado_por: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO decisoes_validadas (tipo_processo, assunto_detectado, documento_escolhido, providencia_aprovada, confianca, aprovado_por) VALUES (?, ?, ?, ?, ?, ?)",
            (tipo_processo, assunto_detectado, documento_escolhido, providencia_aprovada, confianca, aprovado_por)
        )

def list_decisoes_validadas() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM decisoes_validadas")
        return [dict(row) for row in cursor.fetchall()]

def add_regra_aprendizado(nome: str, descricao: str, condicao: str, acao_sugerida: str, confianca_base: float) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO regras_aprendizado (nome, descricao, condicao, acao_sugerida, confianca_base) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, condicao, acao_sugerida, confianca_base)
        )

def list_regras_aprendizado() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM regras_aprendizado")
        return [dict(row) for row in cursor.fetchall()]

def add_auditoria_evento(timestamp: str, event_type: str, process_number_masked: str, process_number_hash: str, action: str, status: str, metadata: dict) -> None:
    with get_connection() as conn:
        metadata_json = json.dumps(metadata)
        conn.execute(
            "INSERT INTO auditoria_eventos (timestamp, event_type, process_number_masked, process_number_hash, action, status, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (timestamp, event_type, process_number_masked, process_number_hash, action, status, metadata_json)
        )

def list_auditoria_eventos() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM auditoria_eventos")
        return [dict(row) for row in cursor.fetchall()]
