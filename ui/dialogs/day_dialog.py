"""
Модальное окно с деталями одного дня СК.

Показывает приход/уход/факт/ЗУП и расхождение.
"""

import tkinter as tk
from tkinter import ttk

from core.sk.constants import (
    SK_DAY_DIALOG_TITLE,
    SK_TOTAL_NEGATIVE,
    SK_TOTAL_OK,
)


class DayDialog(tk.Toplevel):
    """Модальное окно с деталями дня."""

    def __init__(self, parent, fio: str, day):
        super().__init__(parent)
        self.title(SK_DAY_DIALOG_TITLE.format(fio=fio))
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui(fio, day)
        self._center_on_parent(parent)

    def _build_ui(self, fio: str, day):
        """Собирает содержимое окна."""
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=fio,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        rows = (
            ("Дата", _format_date(day)),
            ("Приход", day["income"] or ""),
            ("Уход", day["outcome"] or ""),
            ("Факт", day["fact_text"] or ""),
            ("ЗУП", _format_zup(day)),
        )
        row = 1
        for label, value in rows:
            ttk.Label(frame, text=f"{label}:", width=14).grid(
                row=row, column=0, sticky="w", pady=2
            )
            ttk.Label(frame, text=value).grid(
                row=row, column=1, sticky="w", pady=2
            )
            row += 1

        diff_label = ttk.Label(
            frame,
            text="Расхождение:",
            width=14,
        )
        diff_label.grid(row=row, column=0, sticky="w", pady=(8, 2))

        diff_text = day["diff_text"] or ""
        diff_value = ttk.Label(frame, text=diff_text)
        diff_value.grid(row=row, column=1, sticky="w", pady=(8, 2))

        if diff_text:
            color = _diff_color(day["diff_minutes"])
            if color:
                diff_value.config(foreground=color)

        row += 1

        ttk.Button(
            frame,
            text="Закрыть",
            command=self.destroy,
        ).grid(row=row, column=0, columnspan=2, pady=(16, 0))

    def _center_on_parent(self, parent):
        """Ставит окно по центру родительского."""
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")


def _format_date(day):
    """Дата дня в формате ДД.ММ.ГГГГ."""
    if day["date"] is None:
        return ""
    return day["date"].strftime("%d.%m.%Y")


def _format_zup(day) -> str:
    """Текстовое представление ЗУП."""
    if day["zup"] is None:
        return ""
    return f"{day['zup']:g}"


def _diff_color(minutes):
    """Цвет для недоработки (минус) — красный, для ОК — зелёный."""
    if minutes is None:
        return None
    if minutes < 0:
        return SK_TOTAL_NEGATIVE
    return SK_TOTAL_OK
