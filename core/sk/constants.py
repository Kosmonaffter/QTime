"""Константы пакета СК."""

# ---------- Болид ----------
BOLID_ENCODING = "cp1251"
BOLID_FIO_MARKER = "фамилия"
BOLID_HEADER_MARKER = "дата/время"
BOLID_EVENT_IN = "вход"
BOLID_EVENT_OUT = "выход"
BOLID_DATE_FORMAT = "%d.%m.%Y %H:%M:%S"

# ---------- Табель ----------
TABEL_SECTION_MARKER = "Склад"
TABEL_FIO_COLUMN = 1
TABEL_NAME_COLUMN = 2
TABEL_GRAPH_COLUMN = 5
TABEL_HEADER_MARKER = "Фамилия"

# Текст ошибки при несоответствии дней
ERR_TABEL_DAY_MISMATCH = (
    "В табеле нарушен порядок дней месяца.\n"
    "Ожидается: 1, 2, 3, ...\n"
    "Пропущено число: {missing}\n\n"
    "Проверьте файл табеля."
)

# ---------- График ----------
GRAPH_MAIN = "Основной график"
GRAPH_MAIN_HOURS = 9

GRAPH_WAREHOUSE_PREFIX = "Склад"
GRAPH_WAREHOUSE_HOURS = 12

# ---------- Обед ----------
LUNCH_HOURS = 1

# ---------- Допуски ----------
TOTAL_TOLERANCE_HOURS = 0.5

# ---------- Статусы сверки ----------
STATUS_GREEN = "green"
STATUS_RED = "red"
STATUS_ORANGE = "orange"
STATUS_YELLOW = "yellow"       # нет в Табеле
STATUS_PURPLE = "purple"       # нет в Болиде
STATUS_GRAY = "gray"           # нет данных нигде

STATUS_COLORS = {
    STATUS_GREEN: "#C2F0C2",
    STATUS_RED: "#FFC2C2",
    STATUS_ORANGE: "#EC870B",
    STATUS_YELLOW: "#FFE9A8",
    STATUS_GRAY: "#E6E6E6",
}

# ---------- Сообщения об отсутствии данных ----------
NO_DATA_IN_BOLID = "в Болиде информации нет"
NO_DATA_IN_ZUP = "нет в Табеле"
NO_INCOME = "нет входа"
NO_OUTCOME = "нет выхода"

# ---------- Excel СК: цвета ----------
SK_FONT_LATE_COLOR = "C00000"    # тёмно-красный для недоработки
SK_FONT_LATE_BOLD = True

# ---------- Единицы времени ----------
MINUTES_IN_HOUR = 60
SECONDS_IN_MINUTE = 60

# ---------- Excel СК ----------
SK_TITLE = "Сверка СК"
SK_HEADERS = (
    "Дата",
    "Приход",
    "Уход",
    "Факт",
    "Расхождение",
)
SK_OUT_COL_FIO = 1
SK_OUT_COL_DATE = 1
SK_OUT_COL_INCOME = 2
SK_OUT_COL_OUTCOME = 3
SK_OUT_COL_FACT = 4
SK_OUT_COL_DIFF = 5

# ---------- UI СК ----------
SK_DIALOG_TITLE = "Сверка СК"
SK_MONTH_LABEL = "Месяц:"
SK_YEAR_LABEL = "Год:"
SK_OPEN_BOLID = "Открыть СКУД/БОЛИД (CSV)"
SK_OPEN_TABEL = "Открыть Табель (xls/xlsx)"
SK_PROCESS = "Обработать"
SK_SAVE = "Сохранить СК"

SK_MSG_BOLID_FIRST = "Сначала откройте файл Болида"
SK_MSG_TABEL_FIRST = "Сначала откройте файл Табель"
SK_MSG_PROCESS_FIRST = "Сначала нажмите «Обработать»"
SK_MSG_SAVED = "Файл сохранён:\n{path}"
SK_MSG_NO_DATA = "Нет данных для сверки"
SK_MSG_PROCESSED = "Обработано: {count} чел., {month} {year}"
SK_MSG_BOLID_SELECTED = "Болид: {name}"
SK_MSG_TABEL_SELECTED = "Табель: {name}"

SK_DAY_DIALOG_TITLE = "Детали дня — {fio}"

# ---------- UI цвета СК ----------
SK_TAB_TREE_ROW_HEIGHT = 24
SK_TAB_SEPARATOR_COLOR = "#E0E0E0"

# Цвета ячеек таблицы дней (по статусу дня)
SK_DAY_COLORS = {
    "green": "#C2F0C2",     # ОК
    "red": "#FFC2C2",       # недоработка
    "orange": "#FFE0B3",    # переработка
    "yellow": "#BFE0F5",    # нет в Табеле (голубой)
    "purple": "#D9C2F0",    # нет в Болиде (сиреневый)
    "gray": "#EDEDED",      # нет данных нигде (серый)
}

# Приоритет для окраски строки (сверху — самый важный)
SK_ROW_PRIORITY = ("red", "orange", "yellow", "purple", "green", "gray")

# Цвета текста в итогах (Tkinter — с #)
SK_TOTAL_NEGATIVE = "#C00000"
SK_TOTAL_OK = "#006000"
SK_TOTAL_OVER = "#C07000"

# ---------- Canvas-сетка ----------
SK_CELL_HEIGHT = 24
SK_COL_WIDTH_DAY = 42
SK_COL_WIDTH_FIO = 220
SK_HEADER_BG = "#D9E1F2"
SK_HEADER_FG = "#000000"
SK_HEADER_FONT = ("Segoe UI", 9, "bold")
SK_CELL_FONT = ("Segoe UI", 8)
SK_CELL_BORDER = "#B0B0B0"
SK_EMPTY_CELL_BG = "#FFFFFF"

# ---------- Подсветка под курсором ----------
SK_HOVER_TAG = "hover"
SK_HOVER_COLOR = "#2E7DD1"
SK_HOVER_WIDTH = 2
# ---------- Подсветка выбранной строки ----------
SK_SELECTED_ROW_BG = "#FFF2A8"

# ---------- Фильтры ----------
SK_FILTER_LATE = "Только недоработка"
SK_FILTER_OVER = "Только переработка"
SK_FILTER_STATUSES_LATE = ("red",)
SK_FILTER_STATUSES_OVER = ("orange",)

# ---------- Показ Факт / Табель ----------
SK_SHOW_FACT_LABEL = "Показать Болид"
SK_SHOW_TABEL_LABEL = "Показать Табель"

# Цвета текста в ячейках
SK_FACT_TEXT_COLOR = "#000000"      # чёрный — Болид
SK_TABEL_TEXT_COLOR = "#2E7DD1"     # синий — Табель
