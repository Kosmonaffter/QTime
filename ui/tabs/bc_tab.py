"""
Вкладка БЦ — учёт рабочего времени.

Содержит:
- выбор Файла 1 (Отработанное время);
- выбор даты начала недели (календарь или ручные поля);
- галочка «Учитывать график и опоздания»;
- кнопки «Обработать» / «Сохранить УРВ»;
- таблицу предпросмотра;
- статусную строку.
"""

import tkinter as tk
from datetime import date, timedelta
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from tkcalendar import DateEntry

from core.color_utils import pick_color
from core.constants import (
    DATE_ENTRY_WIDTH,
    DATE_FORMAT_OUT,
    DAYS_IN_WEEK,
    DEFAULT_DAY_MAX,
    DEFAULT_DAY_MIN,
    DEFAULT_MONTH_MAX,
    DEFAULT_MONTH_MIN,
    DEFAULT_START_TIME,
    DEFAULT_WORK_HOURS,
    DEFAULT_YEAR_MAX,
    DEFAULT_YEAR_MIN,
    DIALOG_DEFAULT_FILENAME,
    DIALOG_OPEN_SOURCE,
    DIALOG_SAVE_TARGET,
    DLG_TITLE_DONE,
    DLG_TITLE_ERROR_DATE,
    DLG_TITLE_ERROR_READ,
    DLG_TITLE_ERROR_SAVE,
    DLG_TITLE_WARNING,
    ERR_OLD_FORMAT,
    EXCEL_FILETYPES,
    EXCEL_FILETYPES_SAVE,
    MODE_LABEL_WEEK,
    MODE_LABEL_MONTH,
    MONTH_MODE,
    MONTH_YEAR_LABEL_MONTH,
    MONTH_YEAR_LABEL_YEAR,
    MSG_CANCELLED,
    MSG_FILE_NOT_SELECTED,
    MSG_INVALID_START_DATE,
    MSG_OPEN_SOURCE_FIRST,
    MSG_PROCESSED,
    MSG_PROCESS_FIRST,
    MSG_SAVED,
    MSG_SOURCE_SELECTED,
    OUT_COL_COUNT,
    PAD_L,
    PAD_M,
    PAD_S,
    PAD_XS,
    PANEL_PADDING,
    SCHEDULE_CHECK_LABEL,
    SCHEDULE_CHECK_TOOLTIP,
    SEPARATOR_ROW_COLOR,
    SEPARATOR_ROW_HEIGHT,
    SPINBOX_DAY_WIDTH,
    SPINBOX_MONTH_WIDTH,
    SPINBOX_YEAR_WIDTH,
    STATUS_COLORS,
    STATUS_FG_ACTIVE,
    STATUS_FG_IDLE,
    STATUS_FG_OK,
    TREE_BORDER_COLOR,
    TREE_ROW_HEIGHT,
    TREE_SELECTED_BG,
    TREE_SELECTED_FG,
    WEEK_MODE,
)
from core.errors import humanize_error, humanize_save_error
from core.schedule import empty_evaluation, evaluate_day, Schedule
from core.source_reader import read_source, DATE_MISMATCH_PREFIX
from core.target_writer import write_target
from core.time_utils import calc_total
from ui.dialogs.date_mismatch_dialog import DateMismatchDialog
from ui.schedule_dialog import ScheduleDialog
from ui.tooltip import Tooltip


class BcTab(ttk.Frame):
    """Вкладка БЦ — учёт рабочего времени."""

    def __init__(self, parent):
        super().__init__(parent, padding=PANEL_PADDING)

        self.source_path = None
        self.people = []
        self.schedules = {}
        self._use_schedule_var = tk.BooleanVar(value=False)
        self._use_calendar_var = tk.BooleanVar(value=True)
        self._mode_var = tk.StringVar(value=WEEK_MODE)
        today = date.today()
        self._month_var = tk.StringVar(value=str(today.month))
        self._month_year_var = tk.StringVar(value=str(today.year))
        self._setup_tree_style()
        self._build_controls()
        self._build_preview()

    # ---------- Настройка стиля ----------

    def _setup_tree_style(self):
        """Делает границы и высоту строк в таблице видимыми."""
        style = ttk.Style(self)
        style.configure(
            "Bc.Treeview",
            rowheight=TREE_ROW_HEIGHT,
            bordercolor=TREE_BORDER_COLOR,
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Bc.Treeview.Heading",
            borderwidth=1,
            relief="solid",
        )
        style.map(
            "Bc.Treeview",
            background=[("selected", TREE_SELECTED_BG)],
            foreground=[("selected", TREE_SELECTED_FG)],
        )

    # ---------- Построение интерфейса ----------

    def _build_controls(self):
        """Создаёт верхнюю панель: файл, режим, дата, кнопки."""
        panel = ttk.Frame(self, padding=PANEL_PADDING)
        panel.pack(fill="x")

        ttk.Button(
            panel,
            text="Открыть Файл 1",
            command=self.choose_source,
        ).pack(side="left", padx=PAD_XS)

        ttk.Radiobutton(
            panel,
            text=MODE_LABEL_WEEK,
            variable=self._mode_var,
            value=WEEK_MODE,
            command=self._toggle_mode,
        ).pack(side="left", padx=(PAD_L, PAD_XS))

        ttk.Radiobutton(
            panel,
            text=MODE_LABEL_MONTH,
            variable=self._mode_var,
            value=MONTH_MODE,
            command=self._toggle_mode,
        ).pack(side="left", padx=PAD_XS)

        default_monday = _last_monday()

        self._date_entry = DateEntry(
            panel,
            date_pattern="dd.mm.yyyy",
            width=DATE_ENTRY_WIDTH,
        )
        self._date_entry.set_date(default_monday)

        self._manual_frame = ttk.Frame(panel)
        self._year_var = tk.StringVar(value=str(default_monday.year))
        self._manual_month_var = tk.StringVar(
            value=f"{default_monday.month:02d}"
        )
        self._day_var = tk.StringVar(value=f"{default_monday.day:02d}")

        self._build_manual_inputs()

        ttk.Checkbutton(
            panel,
            text="Ручной ввод",
            variable=self._use_calendar_var,
            command=self._toggle_date_mode,
        ).pack(side="left", padx=PAD_S)

        self._date_entry.pack(side="left")

        self._month_frame = ttk.Frame(panel)
        ttk.Label(
            self._month_frame, text=MONTH_YEAR_LABEL_MONTH
        ).pack(side="left")
        ttk.Spinbox(
            self._month_frame,
            from_=1, to=12, width=4,
            textvariable=self._month_var,
        ).pack(side="left", padx=PAD_XS)
        ttk.Label(
            self._month_frame, text=MONTH_YEAR_LABEL_YEAR
        ).pack(side="left")
        ttk.Spinbox(
            self._month_frame,
            from_=2020, to=2100, width=6,
            textvariable=self._month_year_var,
        ).pack(side="left", padx=PAD_XS)

        self._schedule_cb = ttk.Checkbutton(
            panel,
            text=f"{SCHEDULE_CHECK_LABEL} ?",
            variable=self._use_schedule_var,
        )
        self._schedule_cb.pack(side="left", padx=(PAD_M, 0))
        Tooltip(self._schedule_cb, SCHEDULE_CHECK_TOOLTIP)

        ttk.Button(
            panel,
            text="Обработать",
            command=self.process,
        ).pack(side="left", padx=PAD_L)

        ttk.Button(
            panel,
            text=DIALOG_SAVE_TARGET,
            command=self.save,
        ).pack(side="left")

        self._status = ttk.Label(
            self,
            text=MSG_FILE_NOT_SELECTED,
            foreground=STATUS_FG_IDLE,
        )
        self._status.pack(fill="x", padx=PAD_S, pady=(PAD_XS, 0))

    def _toggle_mode(self):
        """Переключает отображение: неделя или месяц."""
        is_week = self._mode_var.get() == WEEK_MODE

        if is_week:
            self._month_frame.pack_forget()
            if self._use_calendar_var.get():
                self._date_entry.pack(side="left")
            else:
                self._manual_frame.pack(side="left")
        else:
            self._date_entry.pack_forget()
            self._manual_frame.pack_forget()
            self._month_frame.pack(side="left")

    def _build_manual_inputs(self):
        """Создаёт три поля ручного ввода даты."""
        ttk.Spinbox(
            self._manual_frame,
            from_=DEFAULT_YEAR_MIN,
            to=DEFAULT_YEAR_MAX,
            width=SPINBOX_YEAR_WIDTH,
            textvariable=self._year_var,
        ).pack(side="left")
        ttk.Label(self._manual_frame, text="-").pack(side="left")
        ttk.Spinbox(
            self._manual_frame,
            from_=DEFAULT_MONTH_MIN,
            to=DEFAULT_MONTH_MAX,
            width=SPINBOX_MONTH_WIDTH,
            textvariable=self._manual_month_var,
        ).pack(side="left")
        ttk.Label(self._manual_frame, text="-").pack(side="left")
        ttk.Spinbox(
            self._manual_frame,
            from_=DEFAULT_DAY_MIN,
            to=DEFAULT_DAY_MAX,
            width=SPINBOX_DAY_WIDTH,
            textvariable=self._day_var,
        ).pack(side="left")

    def _build_preview(self):
        """Создаёт таблицу предпросмотра результата."""
        frame = ttk.Frame(self, padding=(PAD_S, PAD_XS))
        frame.pack(fill="both", expand=True)

        columns = (
            "fio", "date", "income", "outcome", "total",
            "status_late", "status_incomplete",
        )
        self._tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            style="Bc.Treeview",
        )

        headings = {
            "fio": "ФИО",
            "date": "Дата",
            "income": "Приход",
            "outcome": "Уход",
            "total": "Итого",
            "status_late": "Опоздание",
            "status_incomplete": "Неполная",
        }
        for key, text in headings.items():
            self._tree.heading(key, text=text)

        widths = {
            "fio": 180,
            "date": 110,
            "income": 90,
            "outcome": 90,
            "total": 90,
            "status_late": 150,
            "status_incomplete": 170,
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
        if self._mode_var.get() == MONTH_MODE:
            return
        if self._use_calendar_var.get():
            self._manual_frame.pack_forget()
            self._date_entry.pack(side="left")
        else:
            self._date_entry.pack_forget()
            self._manual_frame.pack(side="left")

    def choose_source(self):
        """Открывает диалог выбора Файла 1."""
        path = filedialog.askopenfilename(
            title=DIALOG_OPEN_SOURCE,
            filetypes=EXCEL_FILETYPES,
        )
        if not path:
            return
        self.source_path = path
        self._status.config(
            text=MSG_SOURCE_SELECTED.format(name=Path(path).name),
            foreground=STATUS_FG_ACTIVE,
        )

    def process(self):
        """Читает Файл 1 и строит предпросмотр."""
        if not self.source_path:
            messagebox.showwarning(
                DLG_TITLE_WARNING,
                MSG_OPEN_SOURCE_FIRST,
            )
            return

        mode = self._mode_var.get()
        if mode == WEEK_MODE:
            start_date = self._read_start_date()
            if start_date is None:
                return
            month = start_date.month
            year = start_date.year
        else:
            month, year = self._read_month_year()
            if month is None or year is None:
                return
            start_date = date(year, month, 1)

        if self._is_old_format():
            messagebox.showerror(
                DLG_TITLE_ERROR_READ,
                ERR_OLD_FORMAT,
            )
            return

        try:
            self.people = read_source(
                self.source_path,
                start_date,
                mode=mode,
                month=month,
                year=year,
            )
        except ValueError as error:
            self._handle_read_error(error, start_date, mode, month, year)
            return
        except Exception as error:
            messagebox.showerror(
                DLG_TITLE_ERROR_READ,
                humanize_error(error),
            )
            return

        if self._use_schedule_var.get():
            self._open_schedule_dialog()
            if self.schedules is None:
                self._reset_after_cancel()
                return
        else:
            self.schedules = {}

        self._fill_preview()
        self._status.config(
            text=MSG_PROCESSED.format(
                count=len(self.people),
                date=start_date.strftime(DATE_FORMAT_OUT),
            ),
            foreground=STATUS_FG_OK,
        )

    def _read_month_year(self):
        """Возвращает (месяц, год) или (None, None)."""
        try:
            month = int(self._month_var.get())
            year = int(self._month_year_var.get())
        except ValueError:
            messagebox.showerror(
                DLG_TITLE_ERROR_DATE,
                MSG_INVALID_START_DATE,
            )
            return None, None
        return month, year

    def _handle_read_error(self, error, start_date, mode, month, year):
        """Обрабатывает ошибки чтения, включая несовпадение дат."""
        assert self.source_path is not None
        assert month is not None
        assert year is not None
        text = str(error)
        if not text.startswith(DATE_MISMATCH_PREFIX):
            messagebox.showerror(
                DLG_TITLE_ERROR_READ,
                humanize_error(error),
            )
            return

        parts = text.split("|")
        file_day = parts[1] if len(parts) > 1 else ""
        selected_day = parts[2] if len(parts) > 2 else start_date.day

        dialog = DateMismatchDialog(
            self,
            file_day=f"{file_day}.{month:02d}.{year}",
            selected_day=f"{selected_day}.{month:02d}.{year}",
        )
        self.wait_window(dialog)

        if dialog.result is None:
            return

        if dialog.result == "file":
            new_start = date(year, month, int(file_day))
        else:
            new_start = start_date

        if not self.source_path:
            return

        try:
            self.people = read_source(
                self.source_path,
                new_start,
                mode=mode,
                month=month,
                year=year,
            )
        except Exception as err:
            messagebox.showerror(
                DLG_TITLE_ERROR_READ,
                humanize_error(err),
            )
            return

    def save(self):
        """Сохраняет итоговый УРВ в выбранный файл."""
        if not self.people:
            messagebox.showwarning(
                DLG_TITLE_WARNING,
                MSG_PROCESS_FIRST,
            )
            return

        path = filedialog.asksaveasfilename(
            title=DIALOG_SAVE_TARGET,
            defaultextension=".xlsx",
            filetypes=EXCEL_FILETYPES_SAVE,
            initialfile=DIALOG_DEFAULT_FILENAME,
        )
        if not path:
            return

        schedules_for_excel = (
            self.schedules
            if self._use_schedule_var.get()
            else {}
        )
        try:
            write_target(self.people, schedules_for_excel, path)
        except Exception as error:
            messagebox.showerror(
                DLG_TITLE_ERROR_SAVE,
                humanize_save_error(error),
            )
            return

        messagebox.showinfo(
            DLG_TITLE_DONE,
            MSG_SAVED.format(path=path),
        )

    # ---------- Вспомогательные ----------

    def _read_start_date(self):
        """Возвращает дату начала недели из выбранного режима."""
        if self._use_calendar_var.get():
            return self._date_entry.get_date()
        try:
            return date(
                int(self._year_var.get()),
                int(self._manual_month_var.get()),
                int(self._day_var.get()),
            )
        except ValueError:
            messagebox.showerror(
                DLG_TITLE_ERROR_DATE,
                MSG_INVALID_START_DATE,
            )
            return None

    def _is_old_format(self) -> bool:
        """Проверяет, что выбран устаревший формат .xls."""
        if not self.source_path:
            return False
        return Path(self.source_path).suffix.lower() == ".xls"

    def _reset_after_cancel(self):
        """Сбрасывает состояние после отмены модалки графиков."""
        self.people = []
        self.schedules = {}
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._status.config(
            text=MSG_CANCELLED,
            foreground=STATUS_FG_IDLE,
        )

    def _fill_preview(self):
        """Заполняет таблицу, окрашивая статусы и блоки."""
        schedules = self._effective_schedules()

        for item in self._tree.get_children():
            self._tree.delete(item)

        self._tree.tag_configure(
            "separator",
            background=SEPARATOR_ROW_COLOR,
            font=("Segoe UI", SEPARATOR_ROW_HEIGHT),
        )
        for status, color in STATUS_COLORS.items():
            self._tree.tag_configure(
                f"status_{status}", background=color
            )

        for index, person in enumerate(self.people):
            base_tag = f"person_{index}"
            self._tree.tag_configure(
                base_tag, background=pick_color(index)
            )
            schedule = schedules.get(person["fio"])

            first_row = True
            for day in person["days"]:
                self._insert_day_row(
                    person["fio"], day, schedule, base_tag, first_row
                )
                first_row = False

            self._tree.insert(
                "",
                "end",
                tags=("separator",),
                values=("",) * OUT_COL_COUNT,
            )

    def _effective_schedules(self):
        """
        Возвращает словарь графиков для предпросмотра.

        Если галочка не стоит — используем дефолтные графики
        для всех сотрудников (09:00, 9 часов).
        """
        if self.schedules:
            return self.schedules
        default = Schedule(
            start_time=DEFAULT_START_TIME,
            hours=DEFAULT_WORK_HOURS,
        )
        return {
            person["fio"]: default for person in self.people
        }

    def _insert_day_row(self, fio, day, schedule, base_tag, is_first):
        """Вставляет одну строку дня с оценкой по графику."""
        income = day["income"] or ""
        outcome = day["outcome"] or ""
        total = calc_total(income, outcome)
        evaluation = self._evaluate(income, outcome, total, schedule)

        tag = base_tag
        if evaluation.priority_status:
            tag = f"status_{evaluation.priority_status}"

        self._tree.insert(
            "",
            "end",
            tags=(tag,),
            values=(
                fio if is_first else "",
                day["date"].strftime(DATE_FORMAT_OUT),
                income,
                outcome,
                total,
                evaluation.status_late,
                evaluation.status_incomplete,
            ),
        )

    def _evaluate(self, income, outcome, total, schedule):
        """Оценивает день, если график задан."""
        if schedule is None:
            return empty_evaluation()
        return evaluate_day(income, outcome, total, schedule)

    def _open_schedule_dialog(self):
        """Открывает модалку настройки графиков."""
        fio_list = [person["fio"] for person in self.people]
        dialog = ScheduleDialog(self, fio_list)
        self.wait_window(dialog)
        self.schedules = dialog.result


def _last_monday() -> date:
    """Возвращает дату прошлого понедельника."""
    today = date.today()
    offset = today.weekday() + DAYS_IN_WEEK
    return today - timedelta(days=offset)
