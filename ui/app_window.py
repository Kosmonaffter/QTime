"""
Главное окно приложения QTime.

Содержит Notebook с двумя вкладками: БЦ и СК.
"""
import threading
import tkinter as tk
from tkinter import ttk

from core.constants import (
    APP_TITLE,
    TAB_BC_TITLE,
    TAB_SK_TITLE,
    UPDATE_CHECK_DELAY_MS,
    WINDOW_ICON_FILE,
    WINDOW_SIZE,
)
from core import updater
from ui.about_dialog import AboutDialog
from ui.help_dialog import HelpDialog
from ui.resource_utils import resource_path
from ui.tabs.bc_tab import BcTab
from ui.tabs.sk_tab import SkTab
from ui.update_dialog import UpdateDialog


class AppWindow(tk.Tk):
    """Главное окно приложения QTime."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self._set_window_icon()

        self._build_menu()
        self._build_notebook()

        self.after(
            UPDATE_CHECK_DELAY_MS,
            self._check_for_updates,
        )

    def _check_for_updates(self):
        """Проверяет обновления в фоне."""
        thread = threading.Thread(
            target=self._update_worker, daemon=True,
        )
        thread.start()

    def _update_worker(self):
        """Проверка в отдельном потоке."""
        has_update, info = updater.check_for_update()
        if has_update and info:
            self.after(0, lambda: self._show_update_dialog(info))

    def _show_update_dialog(self, info):
        """Показывает окно обновления."""
        UpdateDialog(self, info)
    # ---------- Иконка ----------

    def _set_window_icon(self):
        """Устанавливает иконку окна из assets/qtime_icon.ico."""
        icon_path = resource_path(WINDOW_ICON_FILE)
        if not icon_path.exists():
            return
        try:
            self.iconbitmap(str(icon_path))
        except tk.TclError:
            pass

    # ---------- Меню ----------

    def _build_menu(self):
        """Создаёт верхнее меню с кнопками Инструкция / О программе."""
        menu = tk.Menu(self)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(
            label="Инструкция",
            command=self.show_help,
        )
        help_menu.add_command(
            label="О программе",
            command=self.show_about,
        )
        menu.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menu)

    # ---------- Notebook ----------

    def _build_notebook(self):
        """Создаёт Notebook с вкладками БЦ и СК."""
        style = ttk.Style(self)
        style.configure("QTime.TNotebook.Tab", padding=(16, 8))

        notebook = ttk.Notebook(self, style="QTime.TNotebook")
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self._bc_tab = BcTab(notebook)
        self._sk_tab = SkTab(notebook)

        notebook.add(self._bc_tab, text=TAB_BC_TITLE)
        notebook.add(self._sk_tab, text=TAB_SK_TITLE)

    # ---------- Диалоги ----------

    def show_about(self):
        """Открывает окно «О программе»."""
        AboutDialog(self)

    def show_help(self):
        """Открывает окно «Инструкция»."""
        HelpDialog(self)
