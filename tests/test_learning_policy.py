from app.intelligence.learning_policy import register_approved_correction

def test_register_approved_correction_strips_credentials():
    metadata = {
        "user_intent": "correção",
        "password": "123",
        "cookie": "session_cookie"
    }
    result = register_approved_correction("texto erro", "texto certo", metadata)
    assert result["status"] == "correcao_registrada"
    assert "password" not in result["learning_data"]["metadata"]
    assert "cookie" not in result["learning_data"]["metadata"]
