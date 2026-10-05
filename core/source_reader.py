"""
Чтение Файла 1 «Отработанное время за месяц».

Шапка ищется по маркеру (HEADER_MARKER), а не по жёстким координатам.
Это позволяет работать с файлами, где данные начинаются
не со 2-й строки и не с колонки B.
"""

from datetime import date, timedelta

from openpyxl import load_workbook

from core.constants import (
    HEADER_COLUMN_LIMIT,
    HEADER_MARKER,
    HEADER_SEARCH_LIMIT,
    MAX_DAYS,
    RESPONSIBLE_PREFIX,
)
from core.time_utils import parse_cell


def read_source(path: str, start_date: date):
    """
    Читает файл «Отработанное время за месяц».

    start_date — дата первой колонки с данными (обычно понедельник).

    Возвращает список словарей:
    [
        {
            'fio': 'Гайдукевич Людмила',
            'days': [{'date': date(...), 'income': ..., 'outcome': ...}, ...],
        },
        ...
    ]
    """
    workbook = load_workbook(path, data_only=True)
    sheet = workbook.active
    if sheet is None:
        raise ValueError("В файле нет активного листа")

    layout = _find_layout(sheet)
    days_count = _count_days(sheet, layout)
    dates = _build_dates(start_date, days_count)

    people = _read_people(sheet, layout, dates)

    workbook.close()
    return people


# ---------- Поиск шапки ----------

def _find_layout(sheet):
    """
    Находит координаты шапки в файле.

    Возвращает словарь:
    {
        'header_row': 7,       # строка с заголовком
        'first_data_row': 8,   # первая строка с ФИО
        'fio_col': 2,          # колонка с ФИО (B)
        'first_day_col': 3,    # первая колонка с датами (C)
    }

    Если шапка не найдена — выбрасывает ValueError.
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
    """
    Ищет колонку с маркером HEADER_MARKER в указанной строке.

    Возвращает номер колонки или None.
    """
    for col in range(1, HEADER_COLUMN_LIMIT + 1):
        value = sheet.cell(row=row, column=col).value
        if _is_header_cell(value):
            return col
    return None


def _is_header_cell(value) -> bool:
    """
    Проверяет, что значение похоже на заголовок с маркером.

    Регистр не важен, лишние пробелы игнорируются.
    """
    if value is None:
        return False
    text = str(value).strip().lower()
    return HEADER_MARKER in text


# ---------- Подсчёт дней ----------

def _count_days(sheet, layout) -> int:
    """
    Считает, сколько колонок с днями реально заполнено.

    Идём от first_day_col до конца, ищем последнюю заполненную.
    Ограничение — MAX_DAYS. Пустые колонки в конце отбрасываются.
    """
    first = layout["first_day_col"]
    last_filled = first - 1

    for col in range(first, sheet.max_column + 1):
        if _column_has_data(sheet, col, layout):
            last_filled = col

    days = last_filled - first + 1
    if days < 0:
        days = 0
    return min(days, MAX_DAYS)


def _column_has_data(sheet, column: int, layout) -> bool:
    """
    Проверяет, есть ли в колонке хотя бы одно непустое значение.

    Смотрим только строки с данными (ниже шапки).
    """
    start = layout["first_data_row"]
    for row in range(start, sheet.max_row + 1):
        value = sheet.cell(row=row, column=column).value
        if value not in (None, "", "-", "?", "—"):
            return True
    return False


def _build_dates(start_date: date, count: int):
    """Строит список последовательных дат от start_date."""
    return [start_date + timedelta(days=i) for i in range(count)]


# ---------- Чтение людей ----------

def _read_people(sheet, layout, dates):
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

        days = _read_days(sheet, row, layout, dates)
        people.append({"fio": fio, "days": days})
        row += 1

    return people


def _read_fio(sheet, row: int, layout):
    """
    Возвращает ФИО из строки или None, если строка пустая.

    Колонка ФИО берётся из layout.
    """
    raw = sheet.cell(row=row, column=layout["fio_col"]).value
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def _read_days(sheet, row: int, layout, dates):
    """Собирает данные по каждому дню для одного человека."""
    days = []
    first = layout["first_day_col"]

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
