"""
Tkinter-окно приложения QTime.

Содержит выбор Файла 1, выбор даты начала недели
(календарь или ручные поля), предпросмотр и сохранение УРВ.
"""
import sys
import tkinter as tk
from datetime import date, timedelta
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkcalendar import DateEntry

from core.color_utils import pick_color
from core.constants import (
    APP_TITLE,
    DATE_ENTRY_WIDTH,
    DATE_FORMAT_OUT,
    DAYS_IN_WEEK,
    DEFAULT_DAY_MAX,
    DEFAULT_DAY_MIN,
    DEFAULT_MONTH_MAX,
    DEFAULT_MONTH_MIN,
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
    WINDOW_ICON_FILE,
    WINDOW_SIZE,
)
from core.errors import humanize_error, humanize_save_error
from core.source_reader import read_source
from core.schedule import evaluate_day, empty_evaluation
from core.target_writer import write_target
from core.time_utils import calc_total
from ui.about_dialog import AboutDialog
from ui.help_dialog import HelpDialog
from ui.resource_utils import resource_path
from ui.schedule_dialog import ScheduleDialog


class AppWindow(tk.Tk):
    """Главное окно приложения QTime."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self._set_window_icon()

        self.source_path = None
        self.people = []
        self.schedules = {}
        self._use_schedule_var = tk.BooleanVar(value=False)
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
            relief="solid",
        )
        style.configure(
            "QTime.Treeview.Heading",
            borderwidth=1,
            relief="solid",
        )
        style.map(
            "QTime.Treeview",
            background=[("selected", TREE_SELECTED_BG)],
            foreground=[("selected", TREE_SELECTED_FG)],
        )

    def _set_window_icon(self):
        """Устанавливает иконку окна из assets/qtime_icon.ico."""
        icon_path = resource_path(WINDOW_ICON_FILE)
        if not icon_path.exists():
            return
        try:
            self.iconbitmap(str(icon_path))
        except tk.TclError:
            pass

    # ---------- Построение интерфейса ----------

    def _build_controls(self):
        """Создаёт верхнюю панель: файл, дата, кнопки."""
        panel = ttk.Frame(self, padding=PANEL_PADDING)
        panel.pack(fill="x")

        ttk.Button(
            panel,
            text="Открыть Файл 1",
            command=self.choose_source,
        ).pack(side="left", padx=PAD_XS)

        ttk.Label(panel, text="Начало недели (пн):").pack(
            side="left",
            padx=(PAD_L, PAD_XS),
        )

        default_monday = _last_monday()

        self._date_entry = DateEntry(
            panel,
            date_pattern="dd.mm.yyyy",
            width=DATE_ENTRY_WIDTH,
        )
        self._date_entry.set_date(default_monday)

        self._manual_frame = ttk.Frame(panel)
        self._year_var = tk.StringVar(value=str(default_monday.year))
        self._month_var = tk.StringVar(value=f"{default_monday.month:02d}")
        self._day_var = tk.StringVar(value=f"{default_monday.day:02d}")

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
        ).pack(side="left", padx=PAD_S)

        self._date_entry.pack(side="left")

        ttk.Checkbutton(
            panel,
            text=SCHEDULE_CHECK_LABEL,
            variable=self._use_schedule_var,
        ).pack(side="left", padx=(PAD_M, 0))

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

        ttk.Button(
            panel,
            text="Инструкция",
            command=self.show_help,
        ).pack(side="left", padx=(PAD_M, PAD_XS))

        ttk.Button(
            panel,
            text="О программе",
            command=self.show_about,
        ).pack(side="left")

        self._status = ttk.Label(
            self,
            text=MSG_FILE_NOT_SELECTED,
            foreground=STATUS_FG_IDLE,
        )
        self._status.pack(fill="x", padx=PAD_S)

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
            style="QTime.Treeview",
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

        start_date = self._read_start_date()
        if start_date is None:
            return

        if self._is_old_format():
            messagebox.showerror(
                DLG_TITLE_ERROR_READ,
                ERR_OLD_FORMAT,
            )
            return

        try:
            self.people = read_source(self.source_path, start_date)
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

        try:
            write_target(self.people, self.schedules, path)
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
                int(self._month_var.get()),
                int(self._day_var.get()),
            )
        except ValueError:
            messagebox.showerror(
                DLG_TITLE_ERROR_DATE,
                MSG_INVALID_START_DATE,
            )
            return None

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

    def _is_old_format(self) -> bool:
        """Проверяет, что выбран устаревший формат .xls."""
        if not self.source_path:
            return False
        return Path(self.source_path).suffix.lower() == ".xls"

    def _fill_preview(self):
        """Заполняет таблицу, окрашивая статусы и блоки."""
        schedules = self.schedules or {}

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

    def _insert_day_row(self, fio, day, schedule, base_tag, is_first_row):
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
                fio if is_first_row else "",
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

    def show_about(self):
        """Открывает окно «О программе»."""
        AboutDialog(self)

    def show_help(self):
        """Открывает окно «Инструкция»."""
        HelpDialog(self)

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
