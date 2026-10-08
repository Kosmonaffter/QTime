"""
Окно «О программе».

Показывает краткое резюме, технический стек и контакты разработчика.
"""

import tkinter as tk
from tkinter import ttk

from core.constants import LOGO_FILE
from ui.resource_utils import resource_path


ABOUT_TITLE = "О программе QTime"
MAX_LOGO_WIDTH = 400
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
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_on_parent(parent)
        self.update_idletasks()
        self.geometry("")

    def _build_ui(self):
        """Собирает содержимое окна."""
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        self._add_logo(frame)

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

    def _add_logo(self, parent):
        """Добавляет логотип компании, если файл найден."""
        logo_path = resource_path(LOGO_FILE)
        if not logo_path.exists():
            return
        try:
            image = tk.PhotoImage(file=str(logo_path))
        except tk.TclError:
            return

        image = self._fit_logo(image)
        self._logo_image = image
        ttk.Label(parent, image=image).pack(
            anchor="center", pady=(0, 12)
        )

    def _fit_logo(self, image):
        """
        Уменьшает логотип, если он шире MAX_LOGO_WIDTH.

        Возвращает либо исходный, либо уменьшенный через subsample.
        """
        if image.width() <= MAX_LOGO_WIDTH:
            return image
        factor = image.width() // MAX_LOGO_WIDTH + 1
        return image.subsample(factor, factor)

    def _center_on_parent(self, parent):
        """Ставит окно по центру родительского."""
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")
