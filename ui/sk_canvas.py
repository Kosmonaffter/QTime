"""
Canvas-сетка для таблицы дней СК.

Tkinter Treeview не умеет красить отдельные ячейки,
поэтому рисуем сетку вручную: строки — сотрудники,
колонки — дни месяца.
"""

import tkinter as tk
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
)


_VALID_ANCHORS = frozenset(
    {"nw", "n", "ne", "w", "center", "e", "sw", "s", "se"}
)
_AnchorType = Literal[
    "nw", "n", "ne", "w", "center", "e", "sw", "s", "se"
]


class SkDayGrid(tk.Canvas):
    """
    Canvas-сетка: строки = сотрудники, столбцы = дни месяца.

    Поддерживает:
    - цвет ячейки по статусу;
    - клик по ячейке (через callback);
    - вертикальный скролл колесом мыши.
    """

    def __init__(self, parent, on_cell_click=None):
        super().__init__(parent, highlightthickness=0, bg="white")
        self._people = []
        self._month_days = 31
        self._on_cell_click = on_cell_click

        self._bind_events()

    # ---------- Публичный API ----------

    def set_data(self, people, month_days: int):
        """Устанавливает данные и перерисовывает сетку."""
        self._people = people
        self._month_days = month_days
        self._redraw()

    def clear(self):
        """Очищает сетку."""
        self._people = []
        self.delete("all")

    # ---------- События ----------

    def _bind_events(self):
        self.bind("<Configure>", lambda _e: self._redraw())
        self.bind("<Button-1>", self._handle_click)
        self.bind("<MouseWheel>", self._handle_wheel)
        self.bind("<Button-4>", self._handle_wheel)
        self.bind("<Button-5>", self._handle_wheel)

    def _handle_click(self, event):
        """Клик по ячейке."""
        if self._on_cell_click is None:
            return
        cell = self._identify_cell(event.x, event.y)
        if cell is None:
            return
        row_index, day_index = cell
        self._on_cell_click(row_index, day_index)

    def _handle_wheel(self, event):
        """Прокрутка колесом."""
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = -1 if event.delta > 0 else 1
        self.yview_scroll(delta, "units")

    # ---------- Отрисовка ----------

    def _redraw(self):
        """Полная перерисовка сетки."""
        self.delete("all")
        if not self._people:
            return

        total_width = SK_COL_WIDTH_FIO + SK_COL_WIDTH_DAY * self._month_days
        total_height = SK_CELL_HEIGHT * (len(self._people) + 1)

        self.config(scrollregion=(0, 0, total_width, total_height))

        self._draw_header()
        self._draw_rows()

    def _draw_header(self):
        """Рисует шапку с числами дней."""
        self._draw_cell(
            x=0,
            y=0,
            text="ФИО",
            bg=SK_HEADER_BG,
            fg=SK_HEADER_FG,
            font=SK_HEADER_FONT,
            width=SK_COL_WIDTH_FIO,
            anchor="w",
        )
        for day in range(1, self._month_days + 1):
            x = SK_COL_WIDTH_FIO + (day - 1) * SK_COL_WIDTH_DAY
            self._draw_cell(
                x=x,
                y=0,
                text=str(day),
                bg=SK_HEADER_BG,
                fg=SK_HEADER_FG,
                font=SK_HEADER_FONT,
                width=SK_COL_WIDTH_DAY,
            )

    def _draw_rows(self):
        """Рисует строки сотрудников."""
        for row_index, person in enumerate(self._people):
            y = SK_CELL_HEIGHT * (row_index + 1)
            self._draw_person_row(row_index, person, y)

    def _draw_person_row(self, row_index, person, y):
        """Рисует одну строку сотрудника."""
        self._draw_cell(
            x=0,
            y=y,
            text=person["fio"],
            bg="white",
            fg="black",
            font=SK_CELL_FONT,
            width=SK_COL_WIDTH_FIO,
            anchor="w",
            row=row_index,
            col=-1,
        )
        for day_index, day in enumerate(person["days"]):
            if day_index >= self._month_days:
                break
            x = SK_COL_WIDTH_FIO + day_index * SK_COL_WIDTH_DAY
            self._draw_day_cell(x, y, row_index, day_index, day)

    def _draw_day_cell(self, x, y, row_index, day_index, day):
        """Рисует ячейку одного дня."""
        text = _cell_text(day)
        bg = _cell_color(day)
        self._draw_cell(
            x=x,
            y=y,
            text=text,
            bg=bg,
            fg="black",
            font=SK_CELL_FONT,
            width=SK_COL_WIDTH_DAY,
            row=row_index,
            col=day_index,
        )

    def _draw_cell(
        self,
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
        self.create_rectangle(
            x, y, x + width, y + height,
            fill=bg, outline=SK_CELL_BORDER,
        )
        text_x = x + 4 if anchor == "w" else x + width // 2
        anchor_lit = cast(
            _AnchorType,
            anchor if anchor in _VALID_ANCHORS else "center",
        )
        self.create_text(
            text_x, y + height // 2,
            text=text, fill=fg, font=font, anchor=anchor_lit,
        )
        if row >= 0 and col >= 0:
            tag = f"cell_{row}_{col}"
            self.create_rectangle(
                x, y, x + width, y + height,
                fill="", outline="", tags=tag,
            )

    # ---------- Идентификация ----------

    def _identify_cell(self, x: int, y: int):
        """Определяет (row, col) по координатам или None."""
        row = int(y // SK_CELL_HEIGHT) - 1
        if row < 0 or row >= len(self._people):
            return None
        if x < SK_COL_WIDTH_FIO:
            return None
        col = int((x - SK_COL_WIDTH_FIO) // SK_COL_WIDTH_DAY)
        if col < 0 or col >= self._month_days:
            return None
        return row, col


# ---------- Хелперы ----------
def _cell_text(day) -> str:
    """
    Текст ячейки — часы факта или '-'.

    Округляем до 0.5 — полчаса, чтобы попасть в реальную смену.
    """
    fact = day.get("fact_hours")
    if fact is None:
        return "-"
    rounded = round(fact * 2) / 2
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


# ---------- Легенда ----------

_LEGEND_ITEMS = (
    ("green", "всё в порядке"),
    ("red", "недоработка"),
    ("orange", "переработка"),
    ("yellow", "нет в Табеле"),
    ("gray", "нет данных"),
)
