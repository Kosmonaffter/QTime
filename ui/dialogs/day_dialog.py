"""
Модальное окно с деталями одного дня СК.

Показывает приход/уход/факт/Табель и расхождение.
Есть кнопка «Копировать» — копирует всё содержимое.
"""

import tkinter as tk
from tkinter import ttk

from core.sk.constants import (
    SK_DAY_DIALOG_TITLE,
    SK_TOTAL_NEGATIVE,
    SK_TOTAL_OK,
    SK_TOTAL_OVER,
)


class DayDialog(tk.Toplevel):
    """Модальное окно с деталями дня."""

    def __init__(self, parent, fio: str, day):
        super().__init__(parent)
        self.title(SK_DAY_DIALOG_TITLE.format(fio=fio))
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._fio = fio
        self._day = day
        self._build_ui()
        self._center_on_parent(parent)

    def _build_ui(self):
        """Собирает содержимое окна."""
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=self._fio,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        rows = self._build_rows()
        row = 1
        for label, value in rows:
            ttk.Label(frame, text=f"{label}:", width=14).grid(
                row=row, column=0, sticky="w", pady=2
            )
            ttk.Label(frame, text=value).grid(
                row=row, column=1, sticky="w", pady=2
            )
            row += 1

        diff_text = self._day["diff_text"] or ""
        diff_label = ttk.Label(
            frame, text="Расхождение:", width=14,
        )
        diff_label.grid(row=row, column=0, sticky="w", pady=(8, 2))

        diff_value = ttk.Label(frame, text=diff_text)
        diff_value.grid(row=row, column=1, sticky="w", pady=(8, 2))

        if diff_text:
            color = _diff_color(self._day["diff_minutes"])
            if color:
                diff_value.config(foreground=color)

        row += 1

        buttons = ttk.Frame(frame)
        buttons.grid(row=row, column=0, columnspan=2, pady=(16, 0), sticky="e")

        ttk.Button(
            buttons,
            text="Копировать",
            command=self._copy_to_clipboard,
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            buttons,
            text="Закрыть",
            command=self.destroy,
        ).pack(side="left")

    def _build_rows(self):
        """Возвращает список (label, value) для отображения."""
        return (
            ("Дата", _format_date(self._day)),
            ("Приход", self._day["income"] or ""),
            ("Уход", self._day["outcome"] or ""),
            ("Факт", self._day["fact_text"] or ""),
            ("Табель", _format_tabel(self._day)),
        )

    def _copy_to_clipboard(self):
        """Копирует содержимое окна в буфер обмена."""
        lines = [self._fio]
        for label, value in self._build_rows():
            lines.append(f"{label}: {value}")
        lines.append(f"Расхождение: {self._day['diff_text'] or ''}")

        text = "\n".join(lines)
        self.clipboard_clear()
        self.clipboard_append(text)

        # Визуальный фидбек
        self.title(f"{self.title()} — скопировано!")

    def _center_on_parent(self, parent):
        """Ставит окно по центру родительского."""
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")


def _format_date(day) -> str:
    """Дата в формате ДД.ММ.ГГГГ."""
    if day["date"] is None:
        return ""
    return day["date"].strftime("%d.%m.%Y")


def _format_tabel(day) -> str:
    """Табель: 7, 11.5 и т.д."""
    if day["zup"] is None:
        return ""
    return f"{day['zup']:g}"


def _diff_color(minutes):
    """Цвет для расхождения."""
    if minutes is None:
        return None
    if minutes < 0:
        return SK_TOTAL_NEGATIVE
    if minutes > 0:
        return SK_TOTAL_OVER
    return SK_TOTAL_OK
