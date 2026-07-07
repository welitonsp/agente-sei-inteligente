from pathlib import Path
import json
from app.evaluation.shadow_mode import ShadowModeLogger

def test_shadow_mode_logger_records_proposal(tmp_path: Path):
    log_dir = tmp_path / ".shadow_logs"
    logger = ShadowModeLogger(log_dir=str(log_dir))
    
    logger.record_proposal(
        trace_id="test-123",
        processo="20240001",
        intencao="analisar_interesse_19crpm",
        acao_proposta="notificar_comando",
        confidence=98.5,
    )
    
    log_file = log_dir / "shadow_trials.jsonl"
    assert log_file.exists()
    
    with open(log_file, "r", encoding="utf-8") as f:
        data = json.loads(f.readline())
        assert data["trace_id"] == "test-123"
        assert data["processo_sei"] == "20240001"
        assert data["intencao_detectada"] == "analisar_interesse_19crpm"
        assert data["acao_proposta_ia"] == "notificar_comando"
        assert data["confidence_score"] == 98.5
        assert data["acao_real_humano"] is None
        assert data["match"] is None

def test_shadow_mode_logger_records_human_action(tmp_path: Path):
    log_dir = tmp_path / ".shadow_logs"
    logger = ShadowModeLogger(log_dir=str(log_dir))
    
    logger.record_human_action(
        trace_id="test-123",
        acao_real="notificar_comando_e_arquivar"
    )
    
    log_file = log_dir / "shadow_trials.jsonl"
    with open(log_file, "r", encoding="utf-8") as f:
        data = json.loads(f.readline())
        assert data["trace_id"] == "test-123"
        assert data["acao_real_humano"] == "notificar_comando_e_arquivar"
