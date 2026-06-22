import re

def mask_cpf(text: str) -> str:
    # Match CPF patterns like 123.456.789-00
    pattern = r'\b(\d{3})\.?(\d{3})\.?(\d{3})-?(\d{2})\b'
    return re.sub(pattern, r'\1.***.***-\4', text)

def mask_cnpj(text: str) -> str:
    # 12.345.678/0001-90
    pattern = r'\b(\d{2})\.?(\d{3})\.?(\d{3})/?(\d{4})-?(\d{2})\b'
    return re.sub(pattern, r'\1.***.***/\4-\5', text)

def mask_email(text: str) -> str:
    # abc@example.com -> a***@example.com
    pattern = r'\b([a-zA-Z0-9._%+-])[a-zA-Z0-9._%+-]*(@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
    return re.sub(pattern, r'\1***\2', text)

def mask_phone(text: str) -> str:
    # (62) 98888-7777 -> (62) ****-7777
    pattern = r'\(?(\d{2})\)?\s*(9?\d{4})-?(\d{4})\b'
    return re.sub(pattern, r'(\1) ****-\3', text)

def mask_process_number(text: str) -> str:
    # 12345.123456/2024-12 -> 12***.***456/2024-12
    pattern = r'\b(\d{5})\.(\d{6})/(\d{4})-(\d{2})\b'
    return re.sub(pattern, r'\1.***/**\3-\4', text)

def sanitize_text_preview(text: str, max_length: int = 200) -> str:
    if not text:
        return ""
    preview = text[:max_length]
    preview = mask_cpf(preview)
    preview = mask_cnpj(preview)
    preview = mask_email(preview)
    preview = mask_phone(preview)
    preview = mask_process_number(preview)
    if len(text) > max_length:
        preview += "..."
    return preview

def sanitize_metadata(metadata: dict) -> dict:
    forbidden_keys = ["password", "cookie", "token", "session", "full_text"]
    return {k: v for k, v in metadata.items() if k not in forbidden_keys}
