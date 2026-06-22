import sqlite3

def create_tables(conn: sqlite3.Connection):
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS unidades_pmgo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sigla TEXT,
            nome TEXT,
            tipo_unidade TEXT,
            municipio TEXT,
            email_institucional TEXT,
            ativo BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modelos_aprovados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_documento TEXT,
            titulo TEXT,
            conteudo_template TEXT,
            origem TEXT,
            aprovado_por TEXT,
            versao TEXT,
            ativo BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS correcoes_usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_documento TEXT,
            texto_original_hash TEXT,
            texto_corrigido_hash TEXT,
            resumo_correcao TEXT,
            aprovado_por TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisoes_validadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_processo TEXT,
            assunto_detectado TEXT,
            documento_escolhido TEXT,
            providencia_aprovada TEXT,
            confianca REAL,
            aprovado_por TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS regras_aprendizado (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            descricao TEXT,
            condicao TEXT,
            acao_sugerida TEXT,
            confianca_base REAL,
            ativo BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auditoria_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            process_number_masked TEXT,
            process_number_hash TEXT,
            action TEXT,
            status TEXT,
            metadata_json TEXT
        )
    """)
    
    conn.commit()
