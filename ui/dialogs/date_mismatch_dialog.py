"""
Модальное окно несовпадения дат.

Показывается, когда первая дата в Файле 1 не совпадает с выбранной.
"""

import tkinter as tk
from tkinter import ttk

from core.constants import (
    DATE_MISMATCH_BUTTON_CANCEL,
    DATE_MISMATCH_BUTTON_FILE,
    DATE_MISMATCH_BUTTON_SELECTED,
    DATE_MISMATCH_HEADER,
    DATE_MISMATCH_QUESTION,
    DATE_MISMATCH_SELECTED,
    DATE_MISMATCH_TITLE,
)


class DateMismatchDialog(tk.Toplevel):
    """
    Модалка выбора: использовать даты из файла или выбранную.

    Результат (result):
    - 'file' — использовать дату из файла.
    - 'selected' — продолжить с датой пользователя (дни будут пустые).
    - None — отмена.
    """

    def __init__(self, parent, file_day: str, selected_day: str):
        super().__init__(parent)
        self.title(DATE_MISMATCH_TITLE)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result = None
        self._file_day = file_day
        self._selected_day = selected_day

        self._build_ui()
        self._center_on_parent(parent)

    def _build_ui(self):
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=DATE_MISMATCH_HEADER.format(file_date=self._file_day),
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(
            frame,
            text=DATE_MISMATCH_SELECTED.format(
                selected_date=self._selected_day
            ),
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 16))

        ttk.Label(
            frame,
            text=DATE_MISMATCH_QUESTION,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        ttk.Button(
            frame,
            text=f"1. {DATE_MISMATCH_BUTTON_FILE} ({self._file_day})",
            command=lambda: self._finish("file"),
        ).pack(fill="x", pady=2)

        ttk.Button(
            frame,
            text=f"2. {DATE_MISMATCH_BUTTON_SELECTED} ({self._selected_day})",
            command=lambda: self._finish("selected"),
        ).pack(fill="x", pady=2)

        ttk.Button(
            frame,
            text=DATE_MISMATCH_BUTTON_CANCEL,
            command=lambda: self._finish(None),
        ).pack(fill="x", pady=(8, 0))

    def _finish(self, result):
        self.result = result
        self.destroy()

    def _center_on_parent(self, parent):
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.geometry(f"+{x}+{y}")
