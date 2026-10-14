"""
Индикатор новой версии.

Маленькая иконка «!» в углу окна. Появляется только если
на GitHub есть более новая версия.
"""

import tkinter as tk
from tkinter import ttk


class VersionIndicator(ttk.Frame):
    """
    Индикатор новой версии.

    Скрыт по умолчанию. Показывается методом show().
    """

    def __init__(self, parent, on_click=None):
        super().__init__(parent)
        self._on_click = on_click
        self._tooltip = None

        self._button = tk.Label(
            self,
            text="!",
            font=("Segoe UI", 12, "bold"),
            foreground="white",
            background="#E67E22",
            width=2,
            cursor="hand2",
        )
        self._button.pack()
        self._button.bind("<Button-1>", self._handle_click)
        self._button.bind("<Enter>", self._handle_enter)
        self._button.bind("<Leave>", self._handle_leave)

    def show(self, tooltip_text: str):
        """Показывает индикатор с текстом подсказки."""
        self._tooltip_text = tooltip_text
        self.pack(side="right", padx=8, pady=4)

    def hide(self):
        """Скрывает индикатор."""
        self.pack_forget()

    # ---------- События ----------

    def _handle_click(self, _event):
        if self._on_click is not None:
            self._on_click()

    def _handle_enter(self, _event):
        self._show_tooltip()

    def _handle_leave(self, _event):
        self._hide_tooltip()

    # ---------- Tooltip ----------

    def _show_tooltip(self):
        if self._tooltip is not None:
            return
        text = getattr(self, "_tooltip_text", "")
        if not text:
            return
        self._tooltip = tk.Toplevel(self)
        self._tooltip.wm_overrideredirect(True)
        self._tooltip.wm_geometry(
            f"+{self.winfo_rootx()}+{self.winfo_rooty() - 32}"
        )
        tk.Label(
            self._tooltip,
            text=text,
            background="#FFF8DC",
            foreground="#000000",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=8,
            pady=4,
        ).pack()

    def _hide_tooltip(self):
        if self._tooltip is not None:
            self._tooltip.destroy()
            self._tooltip = None
