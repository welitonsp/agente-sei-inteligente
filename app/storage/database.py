import sqlite3
import os
from app.core.config import settings

def get_db_path() -> str:
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        path = db_url.replace("sqlite:///", "")
    else:
        path = "./data/agente19.db"
    return os.path.abspath(path)

def get_connection() -> sqlite3.Connection:
    path = get_db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_database() -> None:
    path = get_db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = get_connection()
    from app.storage.models import create_tables
    create_tables(conn)
    conn.close()
