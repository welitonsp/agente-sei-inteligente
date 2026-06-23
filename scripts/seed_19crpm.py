import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.storage.repositories import add_unidade_pmgo, list_unidades_pmgo

def main():
    print("Semeando unidades iniciais do 19º CRPM no banco local...")
    
    # Check se já tem dados para não duplicar
    unidades = list_unidades_pmgo()
    if len(unidades) > 0:
        print("Banco já contém unidades. Nenhuma alteração realizada.")
        return

    # Seed 19º CRPM
    unidades_iniciais = [
        ("19CRPM", "19º Comando Regional de Polícia Militar", "COMANDO", "Caldas Novas", "19crpm@pm.go.gov.br"),
        ("OFICIAIS", "Grupo de Oficiais do 19º CRPM", "GRUPO", "Caldas Novas", "oficiais.19crpm@pm.go.gov.br"),
        ("36BPM", "36º Batalhão de Polícia Militar", "BATALHAO", "Caldas Novas", "36bpm@pm.go.gov.br"),
        ("BPTUR", "Batalhão de Polícia Turística", "BATALHAO", "Caldas Novas", "bptur@pm.go.gov.br"),
        ("10CIPM", "10ª Companhia Independente de Polícia Militar (CPE)", "COMPANHIA", "Morrinhos", "10cipm@pm.go.gov.br"),
    ]

    for sigla, nome, tipo, municipio, email in unidades_iniciais:
        add_unidade_pmgo(sigla, nome, tipo, municipio, email)
        
    print("Unidades (19º CRPM, 36º BPM, BPTUR, 10ª CIPM/CPE, OFICIAIS) registradas com sucesso.")
    print("Operação concluída de forma segura, sem exposição de credenciais ou dados pessoais.")

if __name__ == "__main__":
    main()
