"""
Информационное окно «Вышла новая версия».

Не скачивает обновление. Показывает инструкцию и кнопку
для открытия страницы релиза в браузере.
"""

import tkinter as tk
import webbrowser
from tkinter import ttk

from core.constants import (
    APP_VERSION,
    UPDATE_BUTTON_LATER,
    UPDATE_BUTTON_OPEN,
    UPDATE_CURRENT,
    UPDATE_DIALOG_TITLE,
    UPDATE_HEADER,
    UPDATE_INSTRUCTION,
    VERSION_RELEASES_URL,
)


class UpdateInfoDialog(tk.Toplevel):
    """Модальное окно с информацией о новой версии."""

    def __init__(self, parent, latest_version: str):
        super().__init__(parent)
        self.title(UPDATE_DIALOG_TITLE)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._latest = latest_version
        self._build_ui()
        self._center_on_parent(parent)

    def _build_ui(self):
        """Собирает содержимое окна."""
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=UPDATE_HEADER.format(version=self._latest),
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(
            frame,
            text=UPDATE_CURRENT.format(version=APP_VERSION),
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 12))

        ttk.Label(
            frame,
            text=UPDATE_INSTRUCTION,
            justify="left",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 16))

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(8, 0))

        ttk.Button(
            buttons,
            text=UPDATE_BUTTON_LATER,
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))

        ttk.Button(
            buttons,
            text=UPDATE_BUTTON_OPEN,
            command=self._open_release_page,
        ).pack(side="right")

    def _open_release_page(self):
        """Открывает страницу релиза в браузере."""
        webbrowser.open(VERSION_RELEASES_URL)

    def _center_on_parent(self, parent):
        """Центрирует окно."""
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.geometry(f"+{x}+{y}")