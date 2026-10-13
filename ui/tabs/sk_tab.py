"""
Вкладка СК — сверка Болида с Табель.

Содержит выбор двух файлов, месяца и года, кнопки Обработать
и Сохранить, таблицу итогов и таблицу дней по горизонтали.
"""

import calendar
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from core.constants import (
    DIALOG_DEFAULT_FILENAME,
    DLG_TITLE_DONE,
    DLG_TITLE_ERROR_READ,
    DLG_TITLE_ERROR_SAVE,
    DLG_TITLE_WARNING,
    PAD_L,
    PAD_M,
    PAD_S,
    PAD_XS,
    PANEL_PADDING,
)
from core.errors import humanize_error, humanize_save_error
from core.sk.bolid_reader import read_bolid
from core.sk.comparator import compare
from core.sk.constants import (
    SK_DAY_COLORS,
    SK_FILTER_LATE,
    SK_FILTER_OVER,
    SK_FILTER_STATUSES_LATE,
    SK_FILTER_STATUSES_OVER,
    SK_MSG_BOLID_FIRST,
    SK_MSG_BOLID_SELECTED,
    SK_MSG_NO_DATA,
    SK_MSG_PROCESS_FIRST,
    SK_MSG_PROCESSED,
    SK_MSG_SAVED,
    SK_MSG_TABEL_FIRST,
    SK_MSG_TABEL_SELECTED,
    SK_MONTH_LABEL,
    SK_OPEN_BOLID,
    SK_OPEN_TABEL,
    SK_PROCESS,
    SK_SAVE,
    SK_SHOW_FACT_LABEL,
    SK_SHOW_TABEL_LABEL,
    SK_TAB_TREE_ROW_HEIGHT,
    SK_TOTAL_NEGATIVE,
    SK_TOTAL_OK,
    SK_YEAR_LABEL,
)
from core.sk.sk_status import (
    day_diff_text,
    format_diff_hours,
    format_fact_total,
    format_tabel_total,
)
from core.sk.sk_writer import write_sk
from core.sk.tabel_reader import read_tabel
from ui.dialogs.day_dialog import DayDialog
from ui.sk_canvas import SkDayGrid, SkLegend


MONTHS_RU = (
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
)

BOLID_FILETYPES = (
    ("CSV", "*.csv"),
    ("Все файлы", "*.*"),
)
TABEL_FILETYPES = (
    ("Excel", "*.xls *.xlsx"),
    ("Все файлы", "*.*"),
)


class SkTab(ttk.Frame):
    """Вкладка СК — сверка Болида с Табель."""

    def __init__(self, parent):
        super().__init__(parent, padding=PANEL_PADDING)

        self.bolid_path = None
        self.tabel_path = None
        self.people = []

        default_month, default_year = _last_month()
        self._month_var = tk.StringVar(
            value=MONTHS_RU[default_month - 1]
        )
        self._year_var = tk.StringVar(value=str(default_year))
        self._filter_late_var = tk.BooleanVar(value=False)
        self._filter_over_var = tk.BooleanVar(value=False)
        self._show_fact_var = tk.BooleanVar(value=True)
        self._show_tabel_var = tk.BooleanVar(value=False)

        self._setup_tree_style()
        self._build_controls()
        self._build_summary()
        self._build_days_table()

    # ---------- Стиль ----------

    def _setup_tree_style(self):
        """Стиль Treeview для вкладки СК."""
        style = ttk.Style(self)
        style.configure(
            "Sk.Treeview",
            rowheight=SK_TAB_TREE_ROW_HEIGHT,
        )
        style.configure(
            "Sk.Treeview.Heading",
            borderwidth=1,
            relief="solid",
        )

    # ---------- Верхняя панель ----------

    def _build_controls(self):
        """Файлы, месяц/год, кнопки."""
        panel = ttk.Frame(self, padding=PANEL_PADDING)
        panel.pack(fill="x")

        ttk.Button(
            panel,
            text=SK_OPEN_BOLID,
            command=self.choose_bolid,
        ).pack(side="left", padx=PAD_XS)

        ttk.Button(
            panel,
            text=SK_OPEN_TABEL,
            command=self.choose_tabel,
        ).pack(side="left", padx=PAD_XS)

        ttk.Label(panel, text=SK_MONTH_LABEL).pack(
            side="left", padx=(PAD_L, PAD_XS)
        )
        ttk.Combobox(
            panel,
            textvariable=self._month_var,
            values=MONTHS_RU,
            width=10,
            state="readonly",
        ).pack(side="left")

        ttk.Label(panel, text=SK_YEAR_LABEL).pack(
            side="left", padx=(PAD_M, PAD_XS)
        )
        ttk.Spinbox(
            panel,
            from_=2020,
            to=2100,
            width=6,
            textvariable=self._year_var,
        ).pack(side="left")

        ttk.Button(
            panel,
            text=SK_PROCESS,
            command=self.process,
        ).pack(side="left", padx=PAD_L)

        ttk.Button(
            panel,
            text=SK_SAVE,
            command=self.save,
        ).pack(side="left")

        filters = ttk.Frame(self, padding=(PANEL_PADDING, 0))
        filters.pack(fill="x")

        ttk.Checkbutton(
            filters,
            text=SK_FILTER_LATE,
            variable=self._filter_late_var,
            command=self._apply_filters,
        ).pack(side="left", padx=PAD_XS)

        ttk.Checkbutton(
            filters,
            text=SK_FILTER_OVER,
            variable=self._filter_over_var,
            command=self._apply_filters,
        ).pack(side="left", padx=PAD_XS)

        ttk.Separator(filters, orient="vertical").pack(
            side="left", fill="y", padx=PAD_M, pady=PAD_XS
        )

        ttk.Checkbutton(
            filters,
            text=SK_SHOW_FACT_LABEL,
            variable=self._show_fact_var,
            command=self._apply_filters,
        ).pack(side="left", padx=PAD_XS)

        ttk.Checkbutton(
            filters,
            text=SK_SHOW_TABEL_LABEL,
            variable=self._show_tabel_var,
            command=self._apply_filters,
        ).pack(side="left", padx=PAD_XS)

        self._status = ttk.Label(
            self,
            text="",
            foreground="gray",
        )
        self._status.pack(fill="x", padx=PAD_S, pady=(PAD_XS, 0))

    # ---------- Таблица итогов ----------

    def _build_summary(self):
        """Таблица итогов: ФИО | Факт | Табель | Расхождение."""
        frame = ttk.Frame(self, padding=(PAD_S, PAD_XS))
        frame.pack(fill="x", expand=False)

        columns = ("fio", "fact", "zup", "diff")
        self._summary = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=8,
            style="Sk.Treeview",
        )

        headings = {
            "fio": "ФИО",
            "fact": "Факт",
            "zup": "Табель",
            "diff": "Расхождение",
        }
        for key, text in headings.items():
            self._summary.heading(key, text=text)

        widths = {
            "fio": 260,
            "fact": 110,
            "zup": 110,
            "diff": 140,
        }
        for key, width in widths.items():
            self._summary.column(key, width=width, anchor="center")

        self._summary.tag_configure("ok", background=SK_DAY_COLORS["green"])
        self._summary.tag_configure("late", background=SK_DAY_COLORS["red"])
        self._summary.tag_configure("over", background=SK_DAY_COLORS["orange"])
        self._summary.tag_configure(
            "missing",
            background=SK_DAY_COLORS["gray"]
        )

        scrollbar = ttk.Scrollbar(
            frame, orient="vertical", command=self._summary.yview
        )
        self._summary.configure(yscrollcommand=scrollbar.set)

        self._summary.pack(side="left", fill="x", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._summary.bind("<<TreeviewSelect>>", self._on_summary_select)

    # ---------- Таблица дней ----------

    def _build_days_table(self):
        """Таблица дней по горизонтали (Canvas-сетка) + легенда."""
        legend = SkLegend(self)
        legend.pack(fill="x", padx=PAD_S)

        wrapper = ttk.Frame(self, padding=(PAD_S, PAD_XS))
        wrapper.pack(fill="both", expand=True)

        self._days = SkDayGrid(
            wrapper,
            on_cell_click=self._on_day_click,
        )
        self._days.pack(fill="both", expand=True)

    # ---------- Действия ----------

    def choose_bolid(self):
        """Открывает диалог выбора CSV Болида."""
        path = filedialog.askopenfilename(
            title="Выберите файл Болида",
            filetypes=BOLID_FILETYPES,
        )
        if not path:
            return
        self.bolid_path = path
        self._status.config(
            text=SK_MSG_BOLID_SELECTED.format(name=Path(path).name),
            foreground="black",
        )

    def choose_tabel(self):
        """Открывает диалог выбора Табеля."""
        path = filedialog.askopenfilename(
            title="Выберите файл Табеля",
            filetypes=TABEL_FILETYPES,
        )
        if not path:
            return
        self.tabel_path = path
        self._status.config(
            text=SK_MSG_TABEL_SELECTED.format(name=Path(path).name),
            foreground="black",
        )

    def process(self):
        """Читает оба файла и строит сверку."""
        if not self.bolid_path:
            messagebox.showwarning(DLG_TITLE_WARNING, SK_MSG_BOLID_FIRST)
            return
        if not self.tabel_path:
            messagebox.showwarning(DLG_TITLE_WARNING, SK_MSG_TABEL_FIRST)
            return

        month, year = self._read_period()
        if month is None or year is None:
            return

        try:
            bolid = read_bolid(self.bolid_path)
            tabel = read_tabel(self.tabel_path, month, year)
        except Exception as error:
            messagebox.showerror(
                DLG_TITLE_ERROR_READ,
                humanize_error(error),
            )
            return

        if not bolid and not tabel:
            messagebox.showinfo(DLG_TITLE_WARNING, SK_MSG_NO_DATA)
            return

        self.people = compare(bolid, tabel, month, year)
        self._fill_summary()
        self._apply_filters()

        self._status.config(
            text=SK_MSG_PROCESSED.format(
                count=len(self.people),
                month=MONTHS_RU[month - 1],
                year=year,
            ),
            foreground=SK_TOTAL_OK,
        )

    def save(self):
        """Сохраняет Excel СК."""
        if not self.people:
            messagebox.showwarning(
                DLG_TITLE_WARNING, SK_MSG_PROCESS_FIRST
            )
            return

        path = filedialog.asksaveasfilename(
            title=SK_SAVE,
            defaultextension=".xlsx",
            filetypes=(("Excel", "*.xlsx"),),
            initialfile=DIALOG_DEFAULT_FILENAME.replace(
                ".xlsx", "_СК.xlsx"
            ),
        )
        if not path:
            return

        try:
            write_sk(self.people, path)
        except Exception as error:
            messagebox.showerror(
                DLG_TITLE_ERROR_SAVE,
                humanize_save_error(error),
            )
            return

        messagebox.showinfo(
            DLG_TITLE_DONE,
            SK_MSG_SAVED.format(path=path),
        )

    # ---------- Заполнение ----------

    def _fill_summary(self):
        """Заполняет таблицу итогов с учётом фильтра."""
        for item in self._summary.get_children():
            self._summary.delete(item)

        visible = self._visible_people()
        for person in visible:
            tag = _summary_tag(person)
            diff_text = format_diff_hours(
                person["total_fact"] - person["total_zup"]
            )
            self._summary.insert(
                "",
                "end",
                iid=person["fio"],
                tags=(tag,),
                values=(
                    person["fio"],
                    format_fact_total(person["total_fact"]),
                    format_tabel_total(person["total_zup"]),
                    diff_text,
                ),
            )

    def _fill_days(self):
        """Заполняет Canvas-сетку дней с учётом фильтра."""
        visible = self._visible_people()
        month_days = self._current_month_days()
        self._days.set_data(
            visible,
            month_days,
            show_fact=self._show_fact_var.get(),
            show_tabel=self._show_tabel_var.get(),
        )

    # ---------- Обработчики ----------

    def _on_summary_select(self, _event):
        """Клик по строке итогов — подсветить в сетке дней."""
        selection = self._summary.selection()
        if not selection:
            return
        fio = selection[0]
        self._days.highlight_person(fio)

    def _on_day_click(self, row_index: int, day_index: int):
        """Клик по ячейке дня — открыть модалку с деталями."""
        visible = self._visible_people()
        if row_index < 0 or row_index >= len(visible):
            return
        person = visible[row_index]
        if day_index < 0 or day_index >= len(person["days"]):
            return
        day = person["days"][day_index]
        if _is_empty_day(day):
            return
        DayDialog(self, person["fio"], day)

    # ---------- Вспомогательные ----------

    def _read_period(self):
        """Возвращает (месяц, год) или (None, None)."""
        try:
            month = MONTHS_RU.index(self._month_var.get()) + 1
            year = int(self._year_var.get())
        except (ValueError, IndexError):
            messagebox.showerror(
                DLG_TITLE_WARNING,
                "Некорректный месяц или год",
            )
            return None, None
        return month, year

    def _apply_filters(self):
        """Пересобирает таблицы с учётом фильтров."""
        if not self.people:
            return
        self._fill_summary()
        self._fill_days()

    def _visible_people(self):
        """
        Возвращает людей, отфильтрованных по галкам.

        Список отсортирован по ФИО.
        """
        filters = []
        if self._filter_late_var.get():
            filters.extend(SK_FILTER_STATUSES_LATE)
        if self._filter_over_var.get():
            filters.extend(SK_FILTER_STATUSES_OVER)

        if filters:
            people = [p for p in self.people if _has_status(p, filters)]
        else:
            people = list(self.people)

        return sorted(people, key=_sort_key)

    def _current_month_days(self) -> int:
        """Число дней в выбранном месяце."""
        month, year = self._read_period()
        if month is None or year is None:
            return 31
        import calendar
        return calendar.monthrange(year, month)[1]


# ---------- Хелперы ----------
def _sort_key(person):
    """Ключ для сортировки по ФИО."""
    return person["fio"].lower().replace("ё", "е")


def _last_month():
    """Возвращает (месяц, год) прошлого месяца."""
    today = date.today()
    month = today.month - 1
    year = today.year
    if month == 0:
        month = 12
        year -= 1
    return month, year


def _summary_tag(person) -> str:
    """
    Тег строки итогов.

    ОК — зелёный, недоработка — красный,
    переработка — оранжевый, нет данных — серый.
    """
    if person["no_zup"] or person["no_bolid"]:
        return "missing"
    if person["total_ok"]:
        return "ok"
    diff = person["total_fact"] - person["total_zup"]
    if diff < 0:
        return "late"
    return "over"


def _is_empty_day(day) -> bool:
    """Пустой день — нет ни Болида, ни Табель."""
    if day["income"] or day["outcome"] or day["zup"] is not None:
        return False
    return day["status"] == "gray"


def _has_status(person, statuses) -> bool:
    """Есть ли у сотрудника хоть один день с нужным статусом."""
    for day in person["days"]:
        if day["status"] in statuses:
            return True
    return False
