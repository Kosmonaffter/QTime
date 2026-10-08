"""
Окно «Инструкция».

Подробное описание работы приложения с пояснением каждой кнопки.
"""

import tkinter as tk
from tkinter import ttk


HELP_TITLE = "Инструкция — QTime"

HELP_SECTIONS = (
    (
        "1. Открыть Файл 1",
        "Нажмите кнопку «Открыть Файл 1» и выберите Excel-файл "
        "«Отработанное время за месяц.xlsx».\n\n"
        "Что должно быть в файле:\n"
        "• Колонка с ФИО сотрудников (заголовок «Фамилия»).\n"
        "• Колонки справа — дни недели с отметками прихода "
        "и ухода.\n"
        "• Строка «Ответственное лицо» — конец данных.\n\n"
        "Формат .xls не поддерживается — сохраните файл как .xlsx.",
    ),
    (
        "2. Дата начала недели",
        "По умолчанию выбирается прошлый понедельник — именно за "
        "него вы обычно делаете отчёт.\n\n"
        "Режимы:\n"
        "• Календарь — кликните по полю и выберите дату.\n"
        "• Ручной ввод — поставьте галочку и введите год, месяц, "
        "день вручную.",
    ),
    (
        "3. Обработать",
        "Нажмите «Обработать». Программа:\n"
        "• прочитает все дни с данными (до 31);\n"
        "• посчитает отработанное время по каждому дню;\n"
        "• покажет результат в таблице предпросмотра.\n\n"
        "Каждый сотрудник выделяется своим цветом.",
    ),
    (
        "4. Графики и опоздания",
        "Поставьте галочку «Учитывать график и опоздания» перед "
        "нажатием «Обработать». Откроется окно, где для каждого "
        "сотрудника задаётся:\n"
        "• Начало смены — время в формате HH:MM.\n"
        "• График — 9 или 12 часов.\n\n"
        "Программа определяет статус дня:\n"
        "• опоздание +0:15 — приход позже начала;\n"
        "• не полная смена −0:30 — отработано меньше нормы;\n"
        "• ОК — всё в порядке.\n\n"
        "Строка красится по приоритету: красный (опоздание) > "
        "оранжевый (не полная смена) > зелёный (ОК).",
    ),
    (
        "5. Сохранить УРВ",
        "Нажмите «Сохранить УРВ» и укажите путь для нового файла.\n\n"
        "Результат — Excel-файл с колонками:\n"
        "ФИО | приход | уход | итого | статус 1 | статус 2 | норма.\n\n"
        "Каждая строка — один рабочий день сотрудника. "
        "Между блоками сотрудников — пустая строка.",
    ),
    (
        "6. Правила расчёта",
        "Если в ячейке два времени — берём первое как приход, "
        "второе как уход.\n\n"
        "Если одно время:\n"
        "• до 13:00 — это приход, уход = «нет выхода»;\n"
        "• после 13:00 — это уход, приход = «нет входа».\n\n"
        "Если нет ни одного — в отчёте будет «ОТСУТСТВОВАЛ».\n\n"
        "Пустые суббота и воскресенье в отчёт не попадают.",
    ),
    (
        "7. О программе",
        "Кнопка «О программе» показывает технический стек, "
        "данные разработчика и контакты.",
    ),
)

CONTACT_LINE = (
    "По вопросам работы программы:\n"
    "GitHub: https://github.com/Kosmonaffter\n"
    "Email: kosmonaffter@yandex.ru\n"
    "Telegram: kosmonafftsb"
)


class HelpDialog(tk.Toplevel):
    """Модальное окно с пошаговой инструкцией."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title(HELP_TITLE)
        self.geometry("640x600")
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        """Собирает прокручиваемое содержимое инструкции."""
        container = ttk.Frame(self, padding=12)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
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

        self._bind_mousewheel(canvas)

        for title, body in HELP_SECTIONS:
            ttk.Label(
                inner,
                text=title,
                font=("Segoe UI", 11, "bold"),
            ).pack(anchor="w", pady=(10, 4))
            ttk.Label(
                inner,
                text=body,
                wraplength=560,
                justify="left",
            ).pack(anchor="w")

        ttk.Separator(inner, orient="horizontal").pack(
            fill="x", pady=12
        )
        ttk.Label(
            inner,
            text=CONTACT_LINE,
            justify="left",
            foreground="#555555",
        ).pack(anchor="w")

        ttk.Button(
            inner,
            text="Понятно",
            command=self.destroy,
        ).pack(anchor="e", pady=12)

    def _bind_mousewheel(self, canvas):
        """
        Привязывает колесо мыши к прокрутке Canvas.

        На Windows/macOS работает <MouseWheel>, на Linux —
        <Button-4>/<Button-5>.
        """
        def _on_wheel(event):
            if event.num == 4:
                delta = -1
            elif event.num == 5:
                delta = 1
            else:
                delta = -1 if event.delta > 0 else 1
            canvas.yview_scroll(delta, "units")

        canvas.bind_all("<MouseWheel>", _on_wheel)
        canvas.bind_all("<Button-4>", _on_wheel)
        canvas.bind_all("<Button-5>", _on_wheel)

    def destroy(self):
        """Отвязывает колесо мыши перед закрытием окна."""
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")
        super().destroy()
