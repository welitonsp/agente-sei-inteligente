"""Testes do leitor ICS (parsing offline, sem rede)."""

from app.integrations.ics_reader import (
    calendar_collision_keys,
    parse_ics,
    unfold,
)

ICS_SAMPLE = (
    "BEGIN:VCALENDAR\r\n"
    "VERSION:2.0\r\n"
    "BEGIN:VEVENT\r\n"
    "UID:abc-123\r\n"
    "SUMMARY:Reuniao de alinhamento\r\n"
    "DTSTART;TZID=America/Sao_Paulo:20260701T090000\r\n"
    "DTEND;TZID=America/Sao_Paulo:20260701T100000\r\n"
    "LOCATION:19 CRPM\r\n"
    "END:VEVENT\r\n"
    "BEGIN:VEVENT\r\n"
    "UID:def-456\r\n"
    "SUMMARY:Feriado municipal com titulo muito longo que foi\r\n"
    " dobrado em duas linhas\r\n"
    "DTSTART;VALUE=DATE:20260702\r\n"
    "END:VEVENT\r\n"
    "END:VCALENDAR\r\n"
)


def test_unfold_junta_linhas_dobradas():
    linhas = unfold("SUMMARY:parte1\r\n parte2")
    assert linhas == ["SUMMARY:parte1parte2"]


def test_parse_evento_com_horario():
    eventos = parse_ics(ICS_SAMPLE)
    assert len(eventos) == 2
    ev = eventos[0]
    assert ev.uid == "abc-123"
    assert ev.summary == "Reuniao de alinhamento"
    assert ev.date == "2026-07-01"
    assert ev.time == "09:00"
    assert ev.location == "19 CRPM"
    assert ev.all_day is False


def test_parse_evento_dia_inteiro_e_dobra_de_linha():
    eventos = parse_ics(ICS_SAMPLE)
    ev = eventos[1]
    assert ev.all_day is True
    assert ev.date == "2026-07-02"
    assert ev.time == ""
    assert ev.summary.endswith("dobrado em duas linhas")


def test_collision_keys_normalizadas():
    eventos = parse_ics(ICS_SAMPLE)
    chaves = calendar_collision_keys(eventos)
    assert "reuniao de alinhamento|2026-07-01|09:00|19 crpm" in chaves
