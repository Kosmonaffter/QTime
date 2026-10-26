"""
Чтение Файла 1 «Отработанное время за месяц».

Шапка ищется по маркеру (HEADER_MARKER), а не по жёстким координатам.

Поддерживает два режима:
- WEEK_MODE: 7 колонок, начиная с выбранной даты (пн).
- MONTH_MODE: все дни месяца (1..N), N — по календарю.
"""

import calendar
from datetime import date, timedelta

from openpyxl import load_workbook

from core.constants import (
    HEADER_COLUMN_LIMIT,
    HEADER_MARKER,
    HEADER_SEARCH_LIMIT,
    MAX_DAYS,
    MONTH_MODE,
    RESPONSIBLE_PREFIX,
    WEEK_MODE,
)
from core.time_utils import parse_cell


DATE_MISMATCH_PREFIX = "_DATE_MISMATCH__"


def read_source(path: str, start_date: date, mode: str = WEEK_MODE,
                month: int = 0, year: int = 0):
    """
    Читает файл «Отработанное время за месяц».

    Режимы:
    - WEEK_MODE: 7 колонок, начиная с start_date.
    - MONTH_MODE: все дни месяца, начиная с 1-го числа.

    Возвращает список словарей:
    [
        {
            'fio': 'Гайдукевич Людмила',
            'days': [{'date': date(...), 'income': ..., 'outcome': ...}, ...],
        },
        ...
    ]

    Если в WEEK_MODE первая дата в файле не совпадает с start_date —
    бросает ValueError с префиксом DATE_MISMATCH_PREFIX.
    """
    workbook = load_workbook(path, data_only=True)
    sheet = workbook.active
    if sheet is None:
        raise ValueError("В файле нет активного листа")

    layout = _find_layout(sheet)
    column_index = _find_day_column(sheet, layout, start_date.day)

    if mode == WEEK_MODE:
        if column_index is None:
            # Выбранной даты нет в файле — модалка
            first_day_number = _first_day_number(sheet, layout)
            raise ValueError(
                f"{DATE_MISMATCH_PREFIX}"
                f"|{first_day_number:02d}"
                f"|{start_date.day:02d}"
            )
        days_count = 7
    else:
        total = calendar.monthrange(year, month)[1]
        days_count = min(total, MAX_DAYS)
        start_date = date(year, month, 1)
        column_index = 0

    dates = _build_dates(start_date, days_count)
    people = _read_people(sheet, layout, dates, column_index)

    workbook.close()
    return people


def _find_day_column(sheet, layout, day_number: int):
    """
    Ищет колонку с указанным днём в шапке.

    Возвращает индекс (0-based) или None, если не найдено.
    """
    header_row = layout["header_row"]
    first_col = layout["first_day_col"]
    last_col = sheet.max_column

    for offset, col in enumerate(range(first_col, last_col + 1)):
        raw = sheet.cell(row=header_row, column=col).value
        number = _parse_day_number(raw)
        if number == day_number:
            return offset
    return None

# ---------- Поиск шапки ----------


def _find_layout(sheet):
    """
    Находит координаты шапки в файле.

    Возвращает словарь:
    {
        'header_row': 7,
        'first_data_row': 8,
        'fio_col': 2,
        'first_day_col': 3,
    }
    """
    for row in range(1, HEADER_SEARCH_LIMIT + 1):
        fio_col = _find_marker_column(sheet, row)
        if fio_col is None:
            continue
        return {
            "header_row": row,
            "first_data_row": row + 1,
            "fio_col": fio_col,
            "first_day_col": fio_col + 1,
        }
    raise ValueError(
        f"Не найдена шапка с маркером '{HEADER_MARKER}' "
        f"в первых {HEADER_SEARCH_LIMIT} строках"
    )


def _find_marker_column(sheet, row: int):
    """Ищет колонку с маркером HEADER_MARKER в строке."""
    for col in range(1, HEADER_COLUMN_LIMIT + 1):
        value = sheet.cell(row=row, column=col).value
        if _is_header_cell(value):
            return col
    return None


def _is_header_cell(value) -> bool:
    """Проверяет, что значение похоже на заголовок с маркером."""
    if value is None:
        return False
    text = str(value).strip().lower()
    return HEADER_MARKER in text


# ---------- Первая дата в файле ----------

def _first_day_number(sheet, layout):
    """
    Возвращает число месяца из первой колонки с датами.

    Берёт значение из шапки, пытается извлечь число
    (например, '19' или '19\\nпн').
    """
    first_col = layout["first_day_col"]
    header_row = layout["header_row"]
    raw = sheet.cell(row=header_row, column=first_col).value
    return _parse_day_number(raw)


def _parse_day_number(value):
    """
    Извлекает число месяца из значения шапки.

    '19' → 19, '19\\nпн' → 19, '19 пн' → 19.
    """
    if value is None:
        return None
    text = str(value).strip()
    first_token = text.split("\n")[0].strip().split(" ")[0].strip()
    try:
        number = int(first_token)
    except ValueError:
        return None
    if 1 <= number <= 31:
        return number
    return None


# ---------- Построение дат ----------

def _build_dates(start_date: date, count: int):
    """Строит список последовательных дат от start_date."""
    return [start_date + timedelta(days=i) for i in range(count)]


# ---------- Чтение людей ----------

def _read_people(sheet, layout, dates, column_index: int = 0):
    """Читает всех сотрудников, начиная со строки данных."""
    people = []
    row = layout["first_data_row"]

    while row <= sheet.max_row:
        fio = _read_fio(sheet, row, layout)
        if fio is None:
            row += 1
            continue
        if fio.lower().startswith(RESPONSIBLE_PREFIX):
            break

        days = _read_days(sheet, row, layout, dates, column_index)
        people.append({"fio": fio, "days": days})
        row += 1

    return people


def _read_fio(sheet, row: int, layout):
    """Возвращает ФИО из строки или None."""
    raw = sheet.cell(row=row, column=layout["fio_col"]).value
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def _read_days(sheet, row: int, layout, dates, column_index: int = 0):
    """Собирает данные по каждому дню для одного человека."""
    days = []
    first = layout["first_day_col"] + column_index

    for index, day_date in enumerate(dates):
        column = first + index
        cell = sheet.cell(row=row, column=column).value
        income, outcome = parse_cell(cell)
        days.append(
            {
                "date": day_date,
                "income": income,
                "outcome": outcome,
                "weekday_index": day_date.weekday(),
            }
        )
    return days
