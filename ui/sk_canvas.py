"""
Canvas-сетка для таблицы дней СК.

Tkinter Treeview не умеет красить отдельные ячейки,
поэтому рисуем сетку вручную: строки — сотрудники,
колонки — дни месяца.
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from typing import Literal, cast

from core.sk.constants import (
    SK_CELL_HEIGHT,
    SK_COL_WIDTH_DAY,
    SK_COL_WIDTH_FIO,
    SK_DAY_COLORS,
    SK_HEADER_BG,
    SK_HEADER_FG,
    SK_HEADER_FONT,
    SK_CELL_BORDER,
    SK_CELL_FONT,
    SK_EMPTY_CELL_BG,
    SK_FACT_TEXT_COLOR,
    SK_TABEL_TEXT_COLOR,
    SK_HOVER_COLOR,
    SK_HOVER_TAG,
    SK_HOVER_WIDTH,
    SK_SELECTED_ROW_BG,
)


_VALID_ANCHORS = frozenset(
    {"nw", "n", "ne", "w", "center", "e", "sw", "s", "se"}
)
_AnchorType = Literal[
    "nw", "n", "ne", "w", "center", "e", "sw", "s", "se"
]


class SkDayGrid(ttk.Frame):
    """
    Canvas-сетка: строки = сотрудники, столбцы = дни месяца.

    Состоит из двух Canvas:
    - header_canvas — фиксированная шапка с числами дней;
    - body_canvas — прокручиваемые строки сотрудников.
    """

    def __init__(self, parent, on_cell_click=None):
        super().__init__(parent)
        self._people = []
        self._month_days = 31
        self._on_cell_click = on_cell_click
        self._highlighted_fio = None
        self._show_fact = True
        self._show_tabel = False
        self._cell_font = tkfont.Font(font=SK_CELL_FONT)
        
        self._build_ui()
        self._bind_events()

    # ---------- Построение ----------

    def _build_ui(self):
        """Создаёт шапку и тело с прокруткой."""
        self._header = tk.Canvas(
            self, highlightthickness=0, bg="white",
            height=SK_CELL_HEIGHT,
        )
        self._header.pack(fill="x")

        body_frame = ttk.Frame(self)
        body_frame.pack(fill="both", expand=True)

        self._body = tk.Canvas(
            body_frame, highlightthickness=0, bg="white",
        )
        scrollbar = ttk.Scrollbar(
            body_frame, orient="vertical", command=self._body.yview,
        )
        self._body.configure(yscrollcommand=scrollbar.set)

        self._body.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _bind_events(self):
        self._body.bind("<Button-1>", self._handle_click)
        self._body.bind("<Motion>", self._handle_motion)
        self._body.bind("<Leave>", self._handle_leave)
        self._body.bind("<MouseWheel>", self._handle_wheel)
        self._body.bind("<Button-4>", self._handle_wheel)
        self._body.bind("<Button-5>", self._handle_wheel)
        self._header.bind("<Button-1>", self._handle_click)

    # ---------- Публичный API ----------

    def set_data(self, people, month_days: int,
                 show_fact: bool = True, show_tabel: bool = False):
        """
        Устанавливает данные и перерисовывает сетку.

        show_fact — показывать число из Болида.
        show_tabel — показывать число из Табеля.
        """
        self._people = people
        self._month_days = month_days
        self._show_fact = show_fact
        self._show_tabel = show_tabel
        fio_list = [p["fio"] for p in people]
        if self._highlighted_fio not in fio_list:
            self._highlighted_fio = None
        self._redraw()

    def clear(self):
        """Очищает сетку."""
        self._people = []
        self._header.delete("all")
        self._body.delete("all")

    def highlight_person(self, fio: str):
        """Подсвечивает всю строку сотрудника по ФИО."""
        self._highlighted_fio = fio
        self._redraw()
        self._scroll_to_fio(fio)

    def _scroll_to_fio(self, fio: str):
        """
        Прокручивает Canvas к строке сотрудника.

        Оставляет 1 пустую строку сверху — чтобы выделенная строка
        не прилипала к шапке. Если строка ниже середины — центрируем.
        """
        index = self._find_person_index(fio)
        if index < 0:
            return
        total_height = SK_CELL_HEIGHT * len(self._people)
        if total_height <= 0:
            return

        visible_height = self._body.winfo_height()
        target_y = SK_CELL_HEIGHT * index

        # Оставляем одну строку запаса сверху
        top_y = max(0, target_y - SK_CELL_HEIGHT)

        # Если строка помещается на экран целиком — не скроллим
        if target_y >= self._body.canvasy(0) and (
            target_y + SK_CELL_HEIGHT
            <= self._body.canvasy(0) + visible_height
        ):
            return

        self._body.yview_moveto(top_y / total_height)

    def _find_person_index(self, fio: str) -> int:
        """Индекс человека в self._people по ФИО."""
        for i, person in enumerate(self._people):
            if person["fio"] == fio:
                return i
        return -1

    # ---------- События ----------

    def _handle_click(self, event):
        """Клик по ячейке."""
        if self._on_cell_click is None:
            return
        canvas_x = int(self._body.canvasx(event.x))
        canvas_y = int(self._body.canvasy(event.y))
        cell = self._identify_cell(canvas_x, canvas_y)
        if cell is None:
            return
        row_index, day_index = cell
        self._on_cell_click(row_index, day_index)

    def _handle_motion(self, event):
        """Подсветка ячейки под курсором."""
        canvas_x = int(self._body.canvasx(event.x))
        canvas_y = int(self._body.canvasy(event.y))
        cell = self._identify_cell(canvas_x, canvas_y)
        if cell is None:
            self._clear_hover()
            return
        row_index, day_index = cell
        self._show_hover(row_index, day_index)

    def _handle_leave(self, _event):
        """Убирает подсветку при уходе курсора с Canvas."""
        self._clear_hover()

    def _handle_wheel(self, event):
        """Прокрутка колесом."""
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = -1 if event.delta > 0 else 1
        self._body.yview_scroll(delta, "units")
        self._clear_hover()

    # ---------- Подсветка ----------

    def _show_hover(self, row_index: int, day_index: int):
        """Рисует рамку вокруг ячейки под курсором."""
        self._clear_hover()
        x = SK_COL_WIDTH_FIO + day_index * SK_COL_WIDTH_DAY
        y = SK_CELL_HEIGHT * row_index
        self._body.create_rectangle(
            x + 1, y + 1,
            x + SK_COL_WIDTH_DAY - 1,
            y + SK_CELL_HEIGHT - 1,
            outline=SK_HOVER_COLOR,
            width=SK_HOVER_WIDTH,
            tags=SK_HOVER_TAG,
        )

    def _clear_hover(self):
        """Удаляет все элементы подсветки."""
        self._body.delete(SK_HOVER_TAG)

    # ---------- Отрисовка ----------

    def _redraw(self):
        """Полная перерисовка: шапка + тело."""
        self._header.delete("all")
        self._body.delete("all")

        if not self._people:
            return

        total_width = SK_COL_WIDTH_FIO + SK_COL_WIDTH_DAY * self._month_days
        total_height = SK_CELL_HEIGHT * len(self._people)

        self._header.config(
            scrollregion=(0, 0, total_width, SK_CELL_HEIGHT)
        )
        self._body.config(scrollregion=(0, 0, total_width, total_height))

        self._draw_header()
        self._draw_rows()

    def _draw_header(self):
        """Рисует шапку с числами дней в header_canvas."""
        self._draw_cell(
            canvas=self._header,
            x=0, y=0,
            text="ФИО",
            bg=SK_HEADER_BG, fg=SK_HEADER_FG, font=SK_HEADER_FONT,
            width=SK_COL_WIDTH_FIO, anchor="w",
        )
        for day in range(1, self._month_days + 1):
            x = SK_COL_WIDTH_FIO + (day - 1) * SK_COL_WIDTH_DAY
            self._draw_cell(
                canvas=self._header,
                x=x, y=0,
                text=str(day),
                bg=SK_HEADER_BG, fg=SK_HEADER_FG, font=SK_HEADER_FONT,
                width=SK_COL_WIDTH_DAY,
            )

    def _draw_rows(self):
        """Рисует строки сотрудников в body_canvas."""
        for row_index, person in enumerate(self._people):
            y = SK_CELL_HEIGHT * row_index
            self._draw_person_row(row_index, person, y)

    def _draw_person_row(self, row_index, person, y):
        """Рисует одну строку сотрудника."""
        is_selected = person["fio"] == self._highlighted_fio
        fio_bg = SK_SELECTED_ROW_BG if is_selected else "white"
        self._draw_cell(
            canvas=self._body,
            x=0, y=y,
            text=person["fio"],
            bg=fio_bg, fg="black", font=SK_CELL_FONT,
            width=SK_COL_WIDTH_FIO, anchor="w",
            row=row_index, col=-1,
        )
        for day_index, day in enumerate(person["days"]):
            if day_index >= self._month_days:
                break
            x = SK_COL_WIDTH_FIO + day_index * SK_COL_WIDTH_DAY
            self._draw_day_cell(x, y, row_index, day_index, day, is_selected)

    def _draw_day_cell(self, x, y, row_index, day_index, day, is_selected):
        """Рисует ячейку одного дня — одно или два числа."""
        bg = _cell_color(day)
        self._draw_cell_bg(x, y, bg)

        fact_text = _fact_text(day) if self._show_fact else None
        tabel_text = _tabel_text(day) if self._show_tabel else None

        if fact_text is not None and tabel_text is not None:
            self._draw_two_values(
                x, y, fact_text, tabel_text,
            )
        elif fact_text is not None:
            self._draw_one_value(x, y, fact_text, SK_FACT_TEXT_COLOR)
        elif tabel_text is not None:
            self._draw_one_value(x, y, tabel_text, SK_TABEL_TEXT_COLOR)

        if is_selected:
            self._body.create_rectangle(
                x + 1, y + 1,
                x + SK_COL_WIDTH_DAY - 1,
                y + SK_CELL_HEIGHT - 1,
                outline=SK_SELECTED_ROW_BG,
                width=2,
            )

    def _draw_cell_bg(self, x: int, y: int, bg: str):
        """Рисует фон ячейки с рамкой."""
        self._body.create_rectangle(
            x, y, x + SK_COL_WIDTH_DAY, y + SK_CELL_HEIGHT,
            fill=bg, outline=SK_CELL_BORDER,
        )

    def _draw_one_value(self, x: int, y: int, text: str, color: str):
        """Рисует одно число по центру ячейки."""
        self._body.create_text(
            x + SK_COL_WIDTH_DAY // 2,
            y + SK_CELL_HEIGHT // 2,
            text=text, fill=color, font=SK_CELL_FONT,
            anchor="center",
        )

    def _draw_two_values(
        self,
        x: int,
        y: int,
        fact_text: str,
        tabel_text: str
    ):
        """
        Рисует два числа через разделитель '|'.

        Первое — Болид (чёрный), второе — Табель (синий).
        Вся группа центрируется по ширине чисел.
        """
        center_y = y + SK_CELL_HEIGHT // 2
        font = self._cell_font

        fact_w = font.measure(fact_text)
        sep_w = font.measure("|")
        tabel_w = font.measure(tabel_text)
        gap = 2  # отступ между числом и разделителем

        total_w = fact_w + gap + sep_w + gap + tabel_w
        start_x = x + (SK_COL_WIDTH_DAY - total_w) // 2

        fact_end = start_x + fact_w
        sep_center = fact_end + gap + sep_w // 2
        tabel_start = sep_center + sep_w // 2 + gap

        self._body.create_text(
            fact_end, center_y,
            text=fact_text, fill=SK_FACT_TEXT_COLOR,
            font=SK_CELL_FONT, anchor="e",
        )
        self._body.create_text(
            sep_center, center_y,
            text="|", fill=SK_CELL_BORDER,
            font=SK_CELL_FONT, anchor="center",
        )
        self._body.create_text(
            tabel_start, center_y,
            text=tabel_text, fill=SK_TABEL_TEXT_COLOR,
            font=SK_CELL_FONT, anchor="w",
        )

    def _draw_cell(
        self,
        canvas,
        x: int,
        y: int,
        text: str,
        bg: str,
        fg: str,
        font,
        width: int,
        anchor: str = "center",
        row: int = -1,
        col: int = -1,
    ):
        """Рисует одну ячейку с рамкой и тегом."""
        height = SK_CELL_HEIGHT
        canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=bg, outline=SK_CELL_BORDER,
        )
        text_x = x + 4 if anchor == "w" else x + width // 2
        anchor_lit = cast(
            _AnchorType,
            anchor if anchor in _VALID_ANCHORS else "center",
        )
        canvas.create_text(
            text_x, y + height // 2,
            text=text, fill=fg, font=font, anchor=anchor_lit,
        )

    # ---------- Идентификация ----------

    def _identify_cell(self, x: int, y: int):
        """Определяет (row, col) по координатам или None."""
        row = int(y // SK_CELL_HEIGHT)
        if row < 0 or row >= len(self._people):
            return None
        if x < SK_COL_WIDTH_FIO:
            return None
        col = int((x - SK_COL_WIDTH_FIO) // SK_COL_WIDTH_DAY)
        if col < 0 or col >= self._month_days:
            return None
        return row, col


# ---------- Хелперы ----------
def _fact_text(day):
    """
    Текст факт-часов из Болида.

    None — если данных нет (не рисуем).
    """
    fact = day.get("fact_hours")
    if fact is None:
        return None
    return _format_hours(fact)


def _tabel_text(day):
    """
    Текст часов из Табеля.

    None — если данных нет.
    """
    tabel = day.get("zup")
    if tabel is None:
        return None
    return _format_hours(tabel)


def _format_hours(value: float) -> str:
    """13.53 → '13.5', 13.0 → '13'."""
    rounded = round(value * 2) / 2
    if rounded == int(rounded):
        return f"{int(rounded)}"
    return f"{rounded:.1f}"


def _cell_color(day) -> str:
    """Цвет ячейки по статусу дня."""
    status = day["status"]
    if status in SK_DAY_COLORS:
        return SK_DAY_COLORS[status]
    return SK_EMPTY_CELL_BG


class SkLegend(ttk.Frame):
    """
    Легенда цветов для Canvas-сетки.

    Показывает: что означает каждый цвет ячейки.
    """

    def __init__(self, parent):
        super().__init__(parent, padding=(4, 6))
        self._build_items()

    def _build_items(self):
        """Строит список цветных квадратиков с подписями."""
        for status, label in _LEGEND_ITEMS:
            self._add_item(status, label)

    def _add_item(self, status: str, label: str):
        """Один цветной квадратик + текст."""
        color = SK_DAY_COLORS.get(status, SK_EMPTY_CELL_BG)
        box = tk.Label(
            self,
            text="  ",
            bg=color,
            borderwidth=1,
            relief="solid",
        )
        box.pack(side="left", padx=(8, 2))
        ttk.Label(self, text=label).pack(side="left", padx=(0, 8))

# ---------- Обозначение для Статуса ----------


_LEGEND_ITEMS = (
    ("green", "всё в порядке"),
    ("red", "недоработка"),
    ("orange", "переработка"),
    ("yellow", "нет в Табеле"),
    ("purple", "нет в Болиде"),
    ("gray", "нет данных"),
)
