import datetime
from datetime import timezone
import hashlib
from typing import Dict, Any, Optional

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
    if process_number:
        process_info = {
            "process_number_hash": get_hash(process_number),
            "process_number_masked": mask_process_number(process_number)
        }
        
    sanitized_metadata = metadata or {}
    
    if "full_text" in sanitized_metadata or "password" in sanitized_metadata or "cookie" in sanitized_metadata:
        sanitized_metadata = {k: v for k, v in sanitized_metadata.items() if k not in ["full_text", "password", "cookie", "token", "session"]}

    event = {
        "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "action": action,
        "status": status,
        "process_info": process_info,
        "metadata": sanitized_metadata
    }
    
    return event
