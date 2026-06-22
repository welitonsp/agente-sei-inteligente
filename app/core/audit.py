import datetime
from datetime import timezone
import hashlib
from typing import Dict, Any, Optional
from app.storage.repositories import add_auditoria_evento

def get_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def mask_process_number(process_number: str) -> str:
    if len(process_number) > 6:
        return process_number[:3] + "***" + process_number[-3:]
    return "***"

def log_audit_event(
    event_type: str,
    action: str,
    status: str,
    process_number: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    
    process_info = None
    process_masked = ""
    process_hash = ""
    if process_number:
        process_masked = mask_process_number(process_number)
        process_hash = get_hash(process_number)
        process_info = {
            "process_number_hash": process_hash,
            "process_number_masked": process_masked
        }
        
    sanitized_metadata = metadata or {}
    
    if "full_text" in sanitized_metadata or "password" in sanitized_metadata or "cookie" in sanitized_metadata or "session" in sanitized_metadata or "token" in sanitized_metadata:
        sanitized_metadata = {k: v for k, v in sanitized_metadata.items() if k not in ["full_text", "password", "cookie", "token", "session"]}

    timestamp_iso = datetime.datetime.now(timezone.utc).isoformat()
    
    event = {
        "timestamp": timestamp_iso,
        "event_type": event_type,
        "action": action,
        "status": status,
        "process_info": process_info,
        "metadata": sanitized_metadata
    }
    
    # Grava no banco de auditoria
    try:
        add_auditoria_evento(timestamp_iso, event_type, process_masked, process_hash, action, status, sanitized_metadata)
    except Exception:
        # Failsafe se o banco não estiver inicializado (ex: em alguns testes)
        pass
    
    return event
