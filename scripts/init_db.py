import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.storage.database import init_database

def main():
    try:
        print("Iniciando a criação do banco de dados seguro do Agente 19...")
        init_database()
        print("Banco SQLite inicializado com sucesso. Tabelas criadas.")
        print("Atenção: Nenhum dado sensível foi exposto no console.")
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {str(e)}")

if __name__ == "__main__":
    main()
