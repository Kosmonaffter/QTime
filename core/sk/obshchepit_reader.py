"""
Чтение Excel-выгрузки событий (Общепит).

Формат: «Системные события». Заголовки в строке 4,
данные с 5-й. Колонки: Время (A), ФИО (D), Событие (J).
"""

import re
from datetime import date, datetime

from openpyxl import load_workbook

from core.sk.constants import (
    BOLID_EVENT_IN,
    BOLID_EVENT_OUT,
)


EVENT_IN_TEXT = "вход по лицу"
EVENT_OUT_TEXT = "выход по лицу"

COL_TIME = 1
COL_FIO = 4
COL_EVENT = 10
HEADER_ROW = 4


def read_obshchepit(path: str):
    """
    Читает Excel с событиями и возвращает структуру как у Болида.

    [{ 'fio': 'Иванов Иван', 'days': {date: {...}} }]
    """
    workbook = load_workbook(path, data_only=True)
    sheet = workbook.active
    if sheet is None:
        raise ValueError("В файле нет активного листа")

    rows = _load_rows(sheet)
    people = _build_people(rows)
    workbook.close()
    return people


def _load_rows(sheet):
    """Возвращает список строк с данными (после заголовка)."""
    rows = []
    for row in sheet.iter_rows(
        min_row=HEADER_ROW + 1, values_only=True
    ):
        if _is_empty_row(row):
            continue
        rows.append(row)
    return rows


def _is_empty_row(row) -> bool:
    """Пустая строка или строка без времени."""
    if not row or len(row) < COL_TIME:
        return True
    time_val = row[COL_TIME - 1]
    return time_val is None or str(time_val).strip() == ""


def _build_people(rows):
    """Группирует строки по ФИО."""
    by_fio = {}
    for row in rows:
        when = _parse_datetime(row[COL_TIME - 1])
        fio = _clean_fio(row[COL_FIO - 1]) if len(row) >= COL_FIO else ""
        event = _parse_event(
            row[COL_EVENT - 1]) if len(row) >= COL_EVENT else None
        if when is None or not fio or event is None:
            continue
        by_fio.setdefault(fio, []).append((when, event))

    people = []
    for fio, events in by_fio.items():
        days = _collect_days(events)
        people.append({"fio": fio, "days": days})
    return people


def _collect_days(events):
    """
    Собирает дни: первая полная смена за день.
    События сортируются по времени.
    """
    events.sort(key=lambda e: e[0])
    days = {}
    for when, event in events:
        d = when.date()
        record = days.setdefault(d, {"income": None, "outcome": None})

        # Логика первой смены
        if event == "in" and record["income"] is None:
            record["income"] = when.strftime("%H:%M:%S")
        elif event == "out" and record["income"] is not None and record["outcome"] is None:
            record["outcome"] = when.strftime("%H:%M:%S")
    return days


def _parse_datetime(value):
    """Парсит '31.10.2026 04:38:35' в datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    for fmt in ("%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    return None


def _clean_fio(value) -> str:
    """Убирает лишние пробелы из ФИО."""
    if value is None:
        return ""
    return " ".join(str(value).split())


def _parse_event(value):
    """'Вход по лицу' -> 'in', 'Выход по лицу' -> 'out'."""
    if value is None:
        return None
    text = str(value).strip().lower()
    if EVENT_IN_TEXT in text:
        return "in"
    if EVENT_OUT_TEXT in text:
        return "out"
    return None
