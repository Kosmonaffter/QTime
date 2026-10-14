"""
Модальное окно обновления QTime.

Показывает новую версию и кнопки Обновить / Позже.
"""

import threading
import tkinter as tk
from tkinter import messagebox, ttk

from core import updater
from core.constants import (
    UPDATE_BUTTON_LATER,
    UPDATE_BUTTON_OPEN,
    UPDATE_BUTTON_UPDATE,
    UPDATE_DIALOG_TITLE,
    UPDATE_DOWNLOADING,
    UPDATE_ERROR,
    UPDATE_HEADER,
    UPDATE_NOTES_LABEL,
    UPDATE_VERSION_TEMPLATE,
)


class UpdateDialog(tk.Toplevel):
    """Модальное окно предложения обновиться."""

    def __init__(self, parent, info: dict):
        super().__init__(parent)
        self.title(UPDATE_DIALOG_TITLE)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._info = info
        self._can_install = updater.can_install_update()

        self._build_ui()
        self._center_on_parent(parent)

    def _build_ui(self):
        """Собирает содержимое окна."""
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=UPDATE_HEADER,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        version_text = UPDATE_VERSION_TEMPLATE.format(
            current=updater.APP_VERSION,
            latest=self._info.get("version", "?"),
        )
        ttk.Label(frame, text=version_text).pack(anchor="w", pady=(0, 8))

        notes_url = self._info.get("release_notes", "")
        if notes_url:
            ttk.Label(
                frame, text=UPDATE_NOTES_LABEL, font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w", pady=(8, 4))

            link = ttk.Label(
                frame, text=notes_url,
                foreground="#2E7DD1", cursor="hand2",
            )
            link.pack(anchor="w")
            link.bind("<Button-1>", lambda _e: _open_url(notes_url))

        buttons = ttk.Frame(frame, padding=(0, 16, 0, 0))
        buttons.pack(fill="x")

        ttk.Button(
            buttons,
            text=UPDATE_BUTTON_LATER,
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))

        if self._can_install:
            ttk.Button(
                buttons,
                text=UPDATE_BUTTON_UPDATE,
                command=self._start_update,
            ).pack(side="right")

        self._status = ttk.Label(frame, text="", foreground="#555555")
        self._status.pack(anchor="w", pady=(8, 0))

    def _start_update(self):
        """Запускает скачивание в отдельном потоке."""
        self._status.config(text=UPDATE_DOWNLOADING)
        thread = threading.Thread(target=self._download_worker, daemon=True)
        thread.start()

    def _download_worker(self):
        """Скачивает и устанавливает обновление."""
        try:
            url = self._info.get("download_url", "")
            if not url:
                raise RuntimeError("Нет ссылки для скачивания")
            updater.download_and_install(url)
        except Exception as error:
            self.after(0, lambda: self._show_error(str(error)))
            return
        self.after(0, self._restart)

    def _show_error(self, text: str):
        """Показывает ошибку."""
        self._status.config(text="")
        messagebox.showerror(
            UPDATE_DIALOG_TITLE,
            UPDATE_ERROR.format(error=text),
        )

    def _restart(self):
        """Закрывает приложение — .bat подхватит."""
        self.destroy()
        updater.restart_application()

    def _center_on_parent(self, parent):
        """Центрирует окно."""
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.geometry(f"+{x}+{y}")


def _open_url(url: str):
    """Открывает URL в браузере."""
    import webbrowser
    webbrowser.open(url)
