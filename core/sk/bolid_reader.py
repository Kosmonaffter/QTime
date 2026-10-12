"""
Чтение CSV-файла от Болида.

Разбирает выгрузку «Маршрут ХО или/и посетителей» в структуру
сотрудников и их дней: {ФИО: {дата: {приход, уход}}}.
"""

import csv
import re
from datetime import date

from core.sk.constants import (
    BOLID_EVENT_IN,
    BOLID_EVENT_OUT,
    BOLID_FIO_MARKER,
    BOLID_ENCODING,
)


EVENT_RE = re.compile(
    r"^(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}):(\d{2}):(\d{2})$"
)


def read_bolid(path: str):
    """
    Читает CSV Болида и возвращает список сотрудников.

    Каждый элемент: {'fio': 'Фамилия Имя', 'days': {date: {...}}}
    """
    rows = _load_rows(path)
    blocks = _split_blocks(rows)
    return [_parse_block(block) for block in blocks]


def _load_rows(path: str):
    """Читает CSV и возвращает список строк (каждая — список колонок)."""
    with open(path, encoding=BOLID_ENCODING, newline="") as f:
        reader = csv.reader(f, delimiter=";", quotechar='"')
        return [row for row in reader]


def _split_blocks(rows):
    """
    Разбивает строки на блоки сотрудников.

    Маркер начала блока — строка с 'фамилия'. Реальная фамилия —
    в следующей строке, в той же колонке.
    """
    blocks = []
    current = None

    for index, row in enumerate(rows):
        marker_col = _find_marker_column(row, BOLID_FIO_MARKER)
        if marker_col is not None:
            if current is not None:
                blocks.append(current)
            surname = _value_below(rows, index, marker_col)
            current = {"surname": surname, "start_row": index, "events": []}
            continue
        if current is not None:
            current["events"].append(row)

    if current is not None:
        blocks.append(current)
    return blocks


def _find_marker_column(row, marker: str):
    """Возвращает индекс колонки с маркером или None."""
    for index, cell in enumerate(row):
        if _clean(cell).lower() == marker.lower():
            return index
    return None


def _value_below(rows, row_index: int, col_index: int) -> str:
    """Возвращает значение из следующей строки в той же колонке."""
    next_index = row_index + 1
    if next_index >= len(rows):
        return ""
    row = rows[next_index]
    if col_index >= len(row):
        return ""
    return _clean(row[col_index])


def _parse_block(block):
    """Преобразует блок в {'fio': ..., 'days': {...}}."""
    surname = block["surname"]
    name = _extract_value(block["events"], "имя")
    fio = f"{surname} {name}".strip()

    days = _collect_days(block["events"])
    return {"fio": fio, "days": days}


def _extract_value(rows, marker: str):
    """
    Ищет маркер в строках блока, возвращает значение из следующей
    строки в той же колонке.
    """
    for index, row in enumerate(rows):
        col = _find_marker_column(row, marker)
        if col is not None:
            return _value_below(rows, index, col)
    return ""


def _collect_days(event_rows):
    """Собирает словарь {дата: {приход, уход}} из строк событий."""
    days = {}

    for row in event_rows:
        when = _find_event_time(row)
        if when is None:
            continue
        event = _find_event_type(row)
        if event is None:
            continue
        day, time_str = when
        record = days.setdefault(day, {"income": None, "outcome": None})
        _update_record(record, event, time_str)

    return days


def _find_event_time(row):
    """Ищет 'ДД.ММ.ГГГГ ЧЧ:ММ:СС'. Возвращает (date, 'HH:MM:SS')."""
    for cell in row:
        match = EVENT_RE.match(_clean(cell))
        if match:
            day = date(
                int(match.group(3)),
                int(match.group(2)),
                int(match.group(1)),
            )
            time_str = f"{match.group(4)}:{match.group(5)}:{match.group(6)}"
            return day, time_str
    return None


def _find_event_type(row):
    """Возвращает 'in' / 'out' / None по строке события."""
    for cell in row:
        value = _clean(cell).lower()
        if value == BOLID_EVENT_IN:
            return "in"
        if value == BOLID_EVENT_OUT:
            return "out"
    return None


def _update_record(record, event: str, time_str: str):
    """Обновляет запись дня: первый вход, последний выход."""
    if event == "in":
        if record["income"] is None or time_str < record["income"]:
            record["income"] = time_str
    elif event == "out":
        if record["outcome"] is None or time_str > record["outcome"]:
            record["outcome"] = time_str


def _clean(value) -> str:
    """Убирает пробелы, приводит к строке."""
    if value is None:
        return ""
    return str(value).strip()
