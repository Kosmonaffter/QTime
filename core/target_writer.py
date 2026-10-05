"""
Запись Файла 2 — итогового табеля УРВ.

Формирует Excel-файл по структуре:
    A: ФИО / дата
    B: приход
    C: уход
    D: итого
"""

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from core.constants import (
    ABSENT,
    BORDER_COLOR,
    COL_WIDTH_FIO,
    COL_WIDTH_TIME,
    COL_WIDTH_TOTAL,
    DATE_FORMAT_OUT,
    HEADER_FIO,
    HEADER_INCOME,
    HEADER_OUTCOME,
    HEADER_TOTAL,
    OUT_COL_FIO,
    WEEKEND_INDEXES,
)
from core.color_utils import (
    header_color,
    pick_color,
    to_excel_color,
)
from core.time_utils import calc_total


def write_target(people, out_path: str):
    """
    Сохраняет итоговый УРВ по списку людей.

    Каждый сотрудник получает свой цвет заливки.
    Пустые выходные (сб, вс) не создают строк.
    Пустые будни создают строку со статусом ОТСУТСТВОВАЛ.
    """
    workbook = Workbook()
    sheet = workbook.active
    if sheet is None:
        raise RuntimeError("Не удалось создать активный лист в книге")
    sheet.title = "УРВ"

    styles = _build_styles()
    row = 1

    for index, person in enumerate(people):
        base = pick_color(index)
        _write_person_header(sheet, row, person["fio"], base, styles)
        row += 1

        for day in person["days"]:
            if _skip_empty_weekend(day):
                continue
            _write_day_row(sheet, row, day, base, styles)
            row += 1

        row += 1    # пустая строка между людьми

    _apply_column_widths(sheet)
    workbook.save(out_path)
    workbook.close()


def _skip_empty_weekend(day) -> bool:
    """
    Проверяет, нужно ли пропустить пустой выходной.

    Пустые сб/вс не попадают в итоговый файл.
    """
    if day["weekday_index"] not in WEEKEND_INDEXES:
        return False
    return not day["income"] and not day["outcome"]


def _build_styles():
    """Возвращает словарь со стилями ячеек."""
    thin = Side(style="thin", color=BORDER_COLOR)
    return {
        "border": Border(left=thin, right=thin, top=thin, bottom=thin),
        "header_font": Font(bold=True),
        "center": Alignment(horizontal="center", vertical="center"),
    }


def _write_person_header(sheet, row: int, fio: str, base_color, styles):
    """Пишет шапку блока человека его цветом."""
    fill = PatternFill(
        "solid",
        fgColor=to_excel_color(header_color(base_color)),
    )
    labels = (HEADER_FIO, HEADER_INCOME, HEADER_OUTCOME, HEADER_TOTAL)
    for offset, label in enumerate(labels):
        column = OUT_COL_FIO + offset
        cell = sheet.cell(row=row, column=column, value=label)
        cell.font = styles["header_font"]
        cell.fill = fill
        cell.alignment = styles["center"]
        cell.border = styles["border"]
    sheet.cell(row=row, column=OUT_COL_FIO, value=fio)


def _write_day_row(sheet, row: int, day, base_color, styles):
    """Пишет строку одного дня, заливая её цветом сотрудника."""
    fill = PatternFill("solid", fgColor=to_excel_color(base_color))

    income = day["income"]
    outcome = day["outcome"]
    total = calc_total(income, outcome)

    values = (
        day["date"].strftime(DATE_FORMAT_OUT),
        _resolve_income_text(income, outcome),
        outcome or "",
        total,
    )
    for offset, value in enumerate(values):
        column = OUT_COL_FIO + offset
        cell = sheet.cell(row=row, column=column, value=value)
        cell.fill = fill
        cell.alignment = styles["center"]
        cell.border = styles["border"]


def _resolve_income_text(income, outcome):
    """
    Определяет, что писать в колонку «приход».

    Если оба значения пустые — считаем, что человек отсутствовал.
    """
    if not income and not outcome:
        return ABSENT
    return income or ""


def _apply_column_widths(sheet):
    """Задаёт ширину колонок итогового файла."""
    sheet.column_dimensions["A"].width = COL_WIDTH_FIO
    sheet.column_dimensions["B"].width = COL_WIDTH_TIME
    sheet.column_dimensions["C"].width = COL_WIDTH_TIME
    sheet.column_dimensions["D"].width = COL_WIDTH_TOTAL
