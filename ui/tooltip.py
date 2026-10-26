"""
Простой tooltip для виджетов Tkinter.

Показывает текст при наведении на виджет.
"""

import tkinter as tk


class Tooltip:
    """
    Всплывающая подсказка для виджета.

    Показывается при наведении курсора.
    """

    def __init__(self, widget, text: str, delay: int = 500):
        self._widget = widget
        self._text = text
        self._delay = delay
        self._tooltip = None
        self._after_id = None

        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _schedule(self, _event=None):
        self._cancel()
        self._after_id = self._widget.after(self._delay, self._show)

    def _cancel(self):
        if self._after_id is not None:
            self._widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self):
        if self._tooltip is not None:
            return
        x = self._widget.winfo_rootx() + 10
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        self._tooltip = tk.Toplevel(self._widget)
        self._tooltip.wm_overrideredirect(True)
        self._tooltip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self._tooltip,
            text=self._text,
            background="#FFFFE0",
            foreground="#000000",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=8,
            pady=4,
            wraplength=320,
            justify="left",
        ).pack()

    def _hide(self, _event=None):
        self._cancel()
        if self._tooltip is not None:
            self._tooltip.destroy()
            self._tooltip = None
