"""
Модальное окно настроек графиков.

Показывает список сотрудников, для каждого — начало смены
и длительность (9 или 12 часов).
"""

import tkinter as tk
from tkinter import ttk

from core.constants import (
    DEFAULT_START_TIME,
    DEFAULT_WORK_HOURS,
    SCHEDULE_DIALOG_APPLY,
    SCHEDULE_DIALOG_CANCEL,
    SCHEDULE_DIALOG_TITLE,
    WORK_HOURS_OPTIONS,
)
from core.schedule import Schedule


# Ширина полей ввода.
START_ENTRY_WIDTH = 8
HOURS_COMBO_WIDTH = 6
DIALOG_WIDTH = 520
DIALOG_HEIGHT = 520


class ScheduleDialog(tk.Toplevel):
    """
    Модальное окно настроек графиков.

    Возвращает словарь {ФИО: Schedule} через result.
    """

    def __init__(self, parent, fio_list):
        super().__init__(parent)
        self.title(SCHEDULE_DIALOG_TITLE)
        self.geometry(f"{DIALOG_WIDTH}x{DIALOG_HEIGHT}")
        self.transient(parent)
        self.grab_set()

        self.result = None
        self._fio_list = fio_list
        self._start_vars = {}
        self._hours_vars = {}

        self._build_ui()

    def _build_ui(self):
        """Собирает шапку, таблицу и кнопки."""
        self._build_header()
        self._build_rows()
        self._build_buttons()

    def _build_header(self):
        """Рисует заголовки колонок."""
        header = ttk.Frame(self, padding=(12, 8, 12, 4))
        header.pack(fill="x")

        ttk.Label(
            header,
            text="ФИО",
            width=30,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")
        ttk.Label(
            header,
            text="Начало",
            width=12,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")
        ttk.Label(
            header,
            text="График",
            width=10,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

    def _build_rows(self):
        """Рисует по строке на каждого сотрудника."""
        container = ttk.Frame(self, padding=(12, 0))
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            container, borderwidth=0, highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            container, orient="vertical", command=canvas.yview
        )
        inner = ttk.Frame(canvas)

        inner.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            ),
        )
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for fio in self._fio_list:
            self._add_row(inner, fio)

    def _add_row(self, parent, fio):
        """Добавляет одну строку: ФИО + начало + график."""
        row = ttk.Frame(parent, padding=(0, 4))
        row.pack(fill="x")

        ttk.Label(row, text=fio, width=30).pack(side="left")

        start_var = tk.StringVar(value=DEFAULT_START_TIME)
        self._start_vars[fio] = start_var
        ttk.Entry(
            row,
            textvariable=start_var,
            width=START_ENTRY_WIDTH,
        ).pack(side="left", padx=(0, 12))

        hours_var = tk.StringVar(value=str(DEFAULT_WORK_HOURS))
        self._hours_vars[fio] = hours_var
        ttk.Combobox(
            row,
            textvariable=hours_var,
            values=[str(h) for h in WORK_HOURS_OPTIONS],
            width=HOURS_COMBO_WIDTH,
            state="readonly",
        ).pack(side="left")

    def _build_buttons(self):
        """Рисует кнопки «Отмена» и «Применить»."""
        panel = ttk.Frame(self, padding=(12, 8))
        panel.pack(fill="x")

        ttk.Button(
            panel,
            text=SCHEDULE_DIALOG_CANCEL,
            command=self._on_cancel,
        ).pack(side="right", padx=4)
        ttk.Button(
            panel,
            text=SCHEDULE_DIALOG_APPLY,
            command=self._on_apply,
        ).pack(side="right")

    def _on_apply(self):
        """Собирает настройки и закрывает окно."""
        schedules = {}
        for fio in self._fio_list:
            start = self._start_vars[fio].get().strip()
            try:
                hours = int(self._hours_vars[fio].get())
            except ValueError:
                hours = DEFAULT_WORK_HOURS
            schedules[fio] = Schedule(start_time=start, hours=hours)

        self.result = schedules
        self.destroy()

    def _on_cancel(self):
        """Закрывает окно без сохранения."""
        self.result = None
        self.destroy()
