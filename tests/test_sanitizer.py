from app.intake.sanitizer import (
    mask_cpf, mask_cnpj, mask_email, mask_phone, mask_process_number, sanitize_text_preview
)

def test_mask_cpf():
    assert mask_cpf("Meu CPF é 123.456.789-00") == "Meu CPF é 123.***.***-00"

def test_mask_cnpj():
    assert mask_cnpj("Empresa 12.345.678/0001-90.") == "Empresa 12.***.***/0001-90."

def test_mask_email():
    assert mask_email("Contato teste@pm.go.gov.br") == "Contato t***@pm.go.gov.br"

def test_mask_phone():
    assert mask_phone("(62) 98888-7777") == "(62) ****-7777"

def test_mask_process_number():
    assert mask_process_number("12345.123456/2024-12") == "12345.***/**2024-12"

def test_sanitize_text_preview():
    text = "O servidor de CPF 123.456.789-00 enviou um email para teste@exemplo.com."
    preview = sanitize_text_preview(text)
    assert "123.456.789-00" not in preview
    assert "123.***.***-00" in preview
    assert "teste@exemplo.com" not in preview
