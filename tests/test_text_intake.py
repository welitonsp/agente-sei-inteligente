from app.intake.text_intake import receive_manual_text

def test_receive_manual_text_returns_hash_only():
    result = receive_manual_text("texto confidencial")
    assert "texto confidencial" not in result.values()
    assert "text_hash" in result
    assert result["char_count"] == 18
