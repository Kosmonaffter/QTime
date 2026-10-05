"""
Утилиты работы со временем.

Парсинг строк времени и расчёт отработанных часов.
"""

import re

from core.constants import (
    EMPTY_MARKS,
    NOON_HOUR,
    NO_INCOME,
    NO_OUTCOME,
    SEPARATOR_RE,
)


TIME_RE = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*$")
MINUTES_IN_HOUR = 60
HOURS_IN_DAY = 24


def parse_time(value: str):
    """
    Преобразует строку '08:58' в кортеж (часы, минуты).

    Возвращает None, если строка не является корректным временем.
    """
    if not value:
        return None
    match = TIME_RE.match(str(value).strip())
    if not match:
        return None
    hours = int(match.group(1))
    minutes = int(match.group(2))
    if not (0 <= hours < HOURS_IN_DAY):
        return None
    if not (0 <= minutes < MINUTES_IN_HOUR):
        return None
    return (hours, minutes)


def _split_head(text: str):
    """
    Отрезает всё после разделителя '------'.

    Возвращает часть ячейки, где лежат только приход и уход.
    """
    parts = re.split(SEPARATOR_RE, text, maxsplit=1)
    return parts[0]


def _extract_valid_lines(text: str):
    """
    Возвращает список непустых строк из головы ячейки.

    Отбрасывает пустые метки вида '-', '?', '—'.
    """
    head = _split_head(text)
    lines = [line.strip() for line in head.split("\n")]
    return [line for line in lines if line and line not in EMPTY_MARKS]


def parse_cell(raw):
    """
    Разбирает содержимое ячейки одного дня.

    Возвращает кортеж (приход, уход):
    - 'HH:MM' — если значение найдено,
    - NO_INCOME / NO_OUTCOME — если одного из них нет,
    - (None, None) — если день пустой (нет ни входа, ни выхода).
    """
    if raw is None:
        return (None, None)

    text = str(raw).replace("\r\n", "\n").replace("\r", "\n")
    lines = _extract_valid_lines(text)

    times = [parse_time(line) for line in lines]
    times = [t for t in times if t is not None]

    if not times:
        return (None, None)

    if len(times) >= 2:
        return (_format_time(times[0]), _format_time(times[1]))

    hours, minutes = times[0]
    if hours < NOON_HOUR:
        return (_format_time((hours, minutes)), NO_OUTCOME)
    return (NO_INCOME, _format_time((hours, minutes)))


def _format_time(pair):
    """(8, 5) -> '08:05'."""
    hours, minutes = pair
    return f"{hours:02d}:{minutes:02d}"


def calc_total(income: str, outcome: str) -> str:
    """
    Считает отработанное время между приходом и уходом.

    Возвращает строку 'HH:MM'. Пустая строка — если посчитать нельзя.
    """
    if not income or not outcome:
        return ""
    if income == NO_INCOME or outcome == NO_OUTCOME:
        return ""

    start = parse_time(income)
    end = parse_time(outcome)
    if not start or not end:
        return ""

    start_min = start[0] * MINUTES_IN_HOUR + start[1]
    end_min = end[0] * MINUTES_IN_HOUR + end[1]

    diff = end_min - start_min
    if diff < 0:
        diff += HOURS_IN_DAY * MINUTES_IN_HOUR

    hours, minutes = divmod(diff, MINUTES_IN_HOUR)
    return f"{hours:02d}:{minutes:02d}"
