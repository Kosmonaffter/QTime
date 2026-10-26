"""
Главное окно приложения QTime.

Содержит Notebook с двумя вкладками: БЦ и СК.
"""
import tkinter as tk
from tkinter import ttk
import threading

from core.constants import (
    APP_TITLE,
    APP_VERSION,
    TAB_BC_TITLE,
    TAB_SK_TITLE,
    VERSION_CHECK_DELAY_MS,
    VERSION_LABEL_TEMPLATE,
    VERSION_NEW_TEMPLATE,
    WINDOW_ICON_FILE,
    WINDOW_SIZE,
)
from core.version_check import check_for_update
from ui.about_dialog import AboutDialog
from ui.dialogs.help_dialog import HelpDialog
from ui.resource_utils import resource_path
from ui.tabs.bc_tab import BcTab
from ui.tabs.sk_tab import SkTab
from ui.update_dialog import UpdateInfoDialog
from ui.version_indicator import VersionIndicator


class AppWindow(tk.Tk):
    """Главное окно приложения QTime."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self._set_window_icon()

        self._latest_version = None

        self._build_menu()
        self._build_notebook()
        self._build_status_bar()

        self.after(
            VERSION_CHECK_DELAY_MS,
            self._start_version_check,
        )
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
    def _build_status_bar(self):
        """Создаёт нижнюю строку с версией и индикатором."""
        self._status_bar = ttk.Frame(self)
        self._status_bar.pack(fill="x", side="bottom")

        self._version_label = ttk.Label(
            self._status_bar,
            text=VERSION_LABEL_TEMPLATE.format(version=APP_VERSION),
            foreground="#777777",
            font=("Segoe UI", 9),
        )
        self._version_label.pack(side="left", padx=8, pady=4)

        self._indicator = VersionIndicator(
            self._status_bar,
            on_click=self._show_update_dialog,
        )
        self._indicator.hide()

    def _start_version_check(self):
        """Запускает проверку версии в фоне."""
        thread = threading.Thread(
            target=self._version_check_worker,
            daemon=True,
        )
        thread.start()

    def _version_check_worker(self):
        """Проверка в отдельном потоке."""
        has_update, latest = check_for_update()
        if has_update and latest:
            self.after(0, lambda: self._on_update_found(latest))

    def _on_update_found(self, latest: str):
        """Показывает индикатор новой версии."""
        self._latest_version = latest
        tooltip = VERSION_NEW_TEMPLATE.format(version=latest)
        self._indicator.show(tooltip)

    def _show_update_dialog(self):
        """Открывает окно информации о новой версии."""
        if self._latest_version:
            UpdateInfoDialog(self, self._latest_version)

    def show_about(self):
        """Открывает окно «О программе»."""
        AboutDialog(self)

    def show_help(self):
        """Открывает окно «Инструкция»."""
        HelpDialog(self)
