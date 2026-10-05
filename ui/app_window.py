"""
Tkinter-окно приложения QTime.

Содержит выбор Файла 1, выбор даты начала недели
(календарь или ручные поля), предпросмотр и сохранение УРВ.
"""

import tkinter as tk
from datetime import date, timedelta
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkcalendar import DateEntry

from core.color_utils import pick_color
from core.constants import (
    APP_TITLE,
    DAYS_IN_WEEK,
    DATE_FORMAT_OUT,
    DEFAULT_DAY_MAX,
    DEFAULT_DAY_MIN,
    DEFAULT_MONTH_MAX,
    DEFAULT_MONTH_MIN,
    DEFAULT_YEAR_MAX,
    DEFAULT_YEAR_MIN,
    STATUS_FG_IDLE,
    STATUS_FG_OK,
    TREE_BORDER_COLOR,
    TREE_ROW_HEIGHT,
    WINDOW_SIZE,
)
from core.source_reader import read_source
from core.target_writer import write_target
from core.time_utils import calc_total
from ui.about_dialog import AboutDialog
from ui.help_dialog import HelpDialog


class AppWindow(tk.Tk):
    """Главное окно приложения QTime."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)

        self.source_path = None
        self.people = []

        self._use_calendar_var = tk.BooleanVar(value=True)

        self._setup_tree_style()
        self._build_controls()
        self._build_preview()

    # ---------- Настройка стиля ----------

    def _setup_tree_style(self):
        """Делает границы и высоту строк в таблице видимыми."""
        style = ttk.Style(self)
        style.configure(
            "QTime.Treeview",
            rowheight=TREE_ROW_HEIGHT,
            bordercolor=TREE_BORDER_COLOR,
            borderwidth=1,
        )
        style.configure(
            "QTime.Treeview.Heading",
            borderwidth=1,
            relief="solid",
        )
        style.map(
            "QTime.Treeview",
            background=[("selected", "#4A90D9")],
            foreground=[("selected", "white")],
        )

    # ---------- Построение интерфейса ----------

    def _build_controls(self):
        """Создаёт верхнюю панель: файл, дата, кнопки."""
        panel = ttk.Frame(self, padding=8)
        panel.pack(fill="x")

        ttk.Button(
            panel,
            text="Открыть Файл 1",
            command=self.choose_source,
        ).pack(side="left", padx=4)

        ttk.Label(panel, text="Начало недели (пн):").pack(
            side="left", padx=(20, 4)
        )

        self._date_entry = DateEntry(
            panel,
            date_pattern="dd.mm.yyyy",
            width=12,
        )
        self._date_entry.set_date(_last_monday())

        self._manual_frame = ttk.Frame(panel)
        default_monday = _last_monday()
        self._year_var = tk.StringVar(value=str(default_monday.year))
        self._month_var = tk.StringVar(value=f"{default_monday.month:02d}")
        self._day_var = tk.StringVar(value=f"{default_monday.day:02d}")

        ttk.Spinbox(
            self._manual_frame,
            from_=DEFAULT_YEAR_MIN,
            to=DEFAULT_YEAR_MAX,
            width=6,
            textvariable=self._year_var,
        ).pack(side="left")
        ttk.Label(self._manual_frame, text="-").pack(side="left")
        ttk.Spinbox(
            self._manual_frame,
            from_=DEFAULT_MONTH_MIN,
            to=DEFAULT_MONTH_MAX,
            width=4,
            textvariable=self._month_var,
        ).pack(side="left")
        ttk.Label(self._manual_frame, text="-").pack(side="left")
        ttk.Spinbox(
            self._manual_frame,
            from_=DEFAULT_DAY_MIN,
            to=DEFAULT_DAY_MAX,
            width=4,
            textvariable=self._day_var,
        ).pack(side="left")

        ttk.Checkbutton(
            panel,
            text="Ручной ввод",
            variable=self._use_calendar_var,
            command=self._toggle_date_mode,
        ).pack(side="left", padx=8)

        self._date_entry.pack(side="left")
        self._manual_frame.pack(side="left")
        self._manual_frame.pack_forget()    # по умолчанию — календарь

        ttk.Button(
            panel,
            text="Обработать",
            command=self.process,
        ).pack(side="left", padx=20)

        ttk.Button(
            panel,
            text="Сохранить УРВ",
            command=self.save,
        ).pack(side="left")

        ttk.Button(
            panel,
            text="Инструкция",
            command=self.show_help,
        ).pack(side="left", padx=(12, 4))

        ttk.Button(
            panel,
            text="О программе",
            command=self.show_about,
        ).pack(side="left")

        self._status = ttk.Label(
            self,
            text="Файл не выбран",
            foreground=STATUS_FG_IDLE,
        )
        self._status.pack(fill="x", padx=8)

    def _build_preview(self):
        """Создаёт таблицу предпросмотра результата."""
        frame = ttk.Frame(self, padding=(8, 4))
        frame.pack(fill="both", expand=True)

        columns = ("fio", "date", "income", "outcome", "total")
        self._tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            style="QTime.Treeview",
        )

        headings = {
            "fio": "ФИО",
            "date": "Дата",
            "income": "Приход",
            "outcome": "Уход",
            "total": "Итого",
        }
        for key, text in headings.items():
            self._tree.heading(key, text=text)

        widths = {
            "fio": 220,
            "date": 120,
            "income": 100,
            "outcome": 100,
            "total": 100,
        }
        for key, width in widths.items():
            self._tree.column(key, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(
            frame, orient="vertical", command=self._tree.yview
        )
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ---------- Действия ----------

    def _toggle_date_mode(self):
        """Переключает между календарём и ручными полями."""
        if self._use_calendar_var.get():
            self._manual_frame.pack_forget()
            self._date_entry.pack(side="left")
        else:
            self._date_entry.pack_forget()
            self._manual_frame.pack(side="left")

    def choose_source(self):
        """Открывает диалог выбора Файла 1."""
        path = filedialog.askopenfilename(
            title="Выберите файл «Отработанное время за месяц»",
            filetypes=(
                ("Excel", "*.xlsx *.xlsm"),
                ("Все файлы", "*.*"),
            ),
        )
        if not path:
            return
        self.source_path = path
        self._status.config(
            text=f"Выбран: {Path(path).name}",
            foreground="black",
        )

    def process(self):
        """Читает Файл 1 и строит предпросмотр."""
        if not self.source_path:
            messagebox.showwarning("Внимание", "Сначала откройте Файл 1")
            return

        start_date = self._read_start_date()
        if start_date is None:
            return

        try:
            self.people = read_source(self.source_path, start_date)
        except Exception as error:
            messagebox.showerror("Ошибка чтения", str(error))
            return

        self._fill_preview()
        self._status.config(
            text=(
                f"Обработано: {len(self.people)} чел., "
                f"с {start_date.strftime(DATE_FORMAT_OUT)}"
            ),
            foreground=STATUS_FG_OK,
        )

    def save(self):
        """Сохраняет итоговый УРВ в выбранный файл."""
        if not self.people:
            messagebox.showwarning(
                "Внимание", "Сначала нажмите «Обработать»"
            )
            return

        path = filedialog.asksaveasfilename(
            title="Сохранить УРВ",
            defaultextension=".xlsx",
            filetypes=(("Excel", "*.xlsx"),),
            initialfile="УРВ.xlsx",
        )
        if not path:
            return

        try:
            write_target(self.people, path)
        except Exception as error:
            messagebox.showerror("Ошибка сохранения", str(error))
            return

        messagebox.showinfo("Готово", f"Сохранено:\n{path}")

    # ---------- Вспомогательные ----------

    def _read_start_date(self):
        """Возвращает дату начала недели из выбранного режима."""
        if self._use_calendar_var.get():
            return self._date_entry.get_date()
        try:
            return date(
                int(self._year_var.get()),
                int(self._month_var.get()),
                int(self._day_var.get()),
            )
        except ValueError:
            messagebox.showerror(
                "Ошибка", "Некорректная дата начала недели"
            )
            return None

    def _fill_preview(self):
        """Заполняет таблицу, окрашивая блоки сотрудников."""
        for item in self._tree.get_children():
            self._tree.delete(item)

        for index, person in enumerate(self.people):
            tag = f"person_{index}"
            color = pick_color(index)
            self._tree.tag_configure(tag, background=color)

            first_row = True
            for day in person["days"]:
                income = day["income"] or ""
                outcome = day["outcome"] or ""
                total = calc_total(income, outcome)
                self._tree.insert(
                    "",
                    "end",
                    tags=(tag,),
                    values=(
                        person["fio"] if first_row else "",
                        day["date"].strftime(DATE_FORMAT_OUT),
                        income,
                        outcome,
                        total,
                    ),
                )
                first_row = False

    def show_about(self):
        """Открывает окно «О программе»."""
        AboutDialog(self)

    def show_help(self):
        """Открывает окно «Инструкция»."""
        HelpDialog(self)


def _last_monday() -> date:
    """Возвращает дату прошлого понедельника."""
    today = date.today()
    offset = today.weekday() + DAYS_IN_WEEK
    return today - timedelta(days=offset)
