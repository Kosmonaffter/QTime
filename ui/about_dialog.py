"""
Окно «О программе».

Показывает краткое резюме, технический стек и контакты разработчика.
"""

import tkinter as tk
from tkinter import ttk


ABOUT_TITLE = "О программе QTime"
ABOUT_HEADER = "QTime — учёт рабочего времени"
ABOUT_SUMMARY = (
    "Десктопное приложение для еженедельной обработки табеля "
    "и формирования УРВ из данных СКУД."
)
ABOUT_STACK = (
    "Python 3.10+\n"
    "Tkinter + tkcalendar\n"
    "openpyxl\n"
    "PyInstaller (сборка EXE)"
)
ABOUT_AUTHOR = (
    "Разработчик: Atlasyuk Uriy Sergeevich\n"
    "GitHub: https://github.com/Kosmonaffter\n"
    "Email: kosmonaffter@yandex.ru\n"
    "Телефон: +7 (926) 375-25-67\n"
    "Telegram: kosmonafftsb\n"
    "Instagram: kosmonaffter"
)
ABOUT_COPYRIGHT = (
    "© 2026 KosmonafftTechnologies. Все права защищены."
)
GITHUB_URL = "https://github.com/Kosmonaffter"


class AboutDialog(tk.Toplevel):
    """Модальное окно с информацией о приложении."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title(ABOUT_TITLE)
        self.geometry("480x520")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        """Собирает содержимое окна."""
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=ABOUT_HEADER,
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(
            frame,
            text=ABOUT_SUMMARY,
            wraplength=440,
            justify="left",
        ).pack(anchor="w", pady=(0, 12))

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=8)

        ttk.Label(
            frame,
            text="Технический стек",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text=ABOUT_STACK,
            justify="left",
        ).pack(anchor="w", pady=(0, 12))

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=8)

        ttk.Label(
            frame,
            text="Контакты",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text=ABOUT_AUTHOR,
            justify="left",
        ).pack(anchor="w", pady=(0, 12))

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=8)

        ttk.Label(
            frame,
            text=ABOUT_COPYRIGHT,
            foreground="gray",
        ).pack(anchor="w", pady=(0, 12))

        ttk.Button(
            frame,
            text="Закрыть",
            command=self.destroy,
        ).pack(side="right")
