"""Módulo de sanitização e anonimização de dados sensíveis (LGPD).

Garante que textos contendo PII (Personal Identifiable Information) 
como CPFs, RGs ou CNPJs sejam redigidos antes de serem enviados
para provedores externos de LLM.
"""

from __future__ import annotations

import re

# Regex patterns para identificação de PII
CPF_PATTERN = re.compile(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b')
CNPJ_PATTERN = re.compile(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b|\b\d{14}\b')
# RG pattern pode variar muito no Brasil, formato mais comum:
RG_PATTERN = re.compile(r'\b\d{1,2}\.\d{3}\.\d{3}-\d{1,2}\b|\b\d{1,2}\.\d{3}\.\d{3}-[A-Za-z0-9]\b')


def mask_cpf(match: re.Match) -> str:
    """Mascarar CPF no formato ***.456.789-** ou ***********."""
    val = match.group(0)
    if "." in val:
        parts = val.split(".")
        if len(parts) == 3 and "-" in parts[2]:
            mid, end = parts[1], parts[2].split("-")[0]
            return f"***.{mid}.{end}-**"
    return "***" + val[3:9] + "**" if len(val) == 11 else "***.***.***-**"


def mask_cnpj(match: re.Match) -> str:
    """Mascarar CNPJ."""
    return "**.***.***/****-**"


def mask_rg(match: re.Match) -> str:
    """Mascarar RG."""
    return "**.***.***-*"


def sanitize_text(text: str) -> str:
    """
    Substitui padrões identificáveis por máscaras de anonimização.
    
    Args:
        text (str): O texto original extraído do SEI.
        
    Returns:
        str: Texto sanitizado, seguro para ser enviado a LLMs não locais.
    """
    if not text:
        return text

    sanitized = CPF_PATTERN.sub(mask_cpf, text)
    sanitized = CNPJ_PATTERN.sub(mask_cnpj, sanitized)
    sanitized = RG_PATTERN.sub(mask_rg, sanitized)
    return sanitized
