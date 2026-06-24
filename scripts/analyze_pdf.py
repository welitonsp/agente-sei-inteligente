import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.intake.pdf_pipeline import process_pdf_file
from app.intelligence.institutional_analyzer import analyze_pdf_pipeline_result

def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/analyze_pdf.py <caminho_do_pdf>")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    
    print(f"Iniciando análise segura do arquivo: {os.path.basename(pdf_path)}")
    print("Atenção: O texto integral não será exibido ou salvo.\n")
    
    pipeline_result = process_pdf_file(pdf_path)
    
    if pipeline_result.get("status") != "sucesso":
        print(f"Falha no processamento: {pipeline_result.get('reason')}")
        sys.exit(1)
        
    analysis_result = analyze_pdf_pipeline_result(pipeline_result)
    
    print("=== Resultado da Análise Institucional ===")
    print(f"Status do Arquivo: SUCESSO")
    print(f"Páginas lidas: {pipeline_result.get('page_count')}")
    print(f"OCR Necessário: {pipeline_result.get('ocr_required')}")
    print("-" * 40)
    print(f"Tipo Provável: {analysis_result.get('tipo_provavel')}")
    print(f"Resumo da Ação: {analysis_result.get('resumo_curto')}")
    print(f"Providência Sugerida: {analysis_result.get('providencia_sugerida')}")
    print(f"Tem Prazo? {'Sim' if analysis_result.get('prazo_detectado') else 'Não'}")
    for prazo in analysis_result.get("prazos", []):
        limite = f" | data-limite: {prazo['data_limite']}" if prazo.get("data_limite") else ""
        print(f"   - Prazo identificado: {prazo['descricao']} ({prazo['tipo']}){limite}")
    print(f"Confiança: {analysis_result.get('confianca')}")
    print("-" * 40)
    print(f"Preview Seguro (Higienizado):\n{pipeline_result.get('safe_preview')}")
    
    print("\n[INFO] Análise concluída. Texto bruto expurgado da memória.")

if __name__ == "__main__":
    main()
