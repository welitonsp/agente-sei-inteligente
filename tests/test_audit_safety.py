from app.core.audit import log_audit_event

def test_log_audit_event_sanitizes_metadata():
    metadata = {
        "some_data": "ok",
        "password": "secret_password",
        "cookie": "secret_cookie",
        "full_text": "text integral sensível"
    }
    
    event = log_audit_event("TEST_EVENT", "test_action", "success", "123456789", metadata)
    
    assert "some_data" in event["metadata"]
    assert "password" not in event["metadata"]
    assert "cookie" not in event["metadata"]
    assert "full_text" not in event["metadata"]
    
def test_log_audit_masks_process_number():
    event = log_audit_event("TEST_EVENT", "test_action", "success", "123456789")
    assert event["process_info"]["process_number_masked"] == "123***789"
