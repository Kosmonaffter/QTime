"""
Константы приложения QTime.

Здесь собраны все «магические» значения и текстовые метки,
чтобы их можно было менять в одном месте.
"""

# ---------- Общие ----------
APP_TITLE = "QTime — учёт рабочего времени"
WINDOW_SIZE = "1100x700"
WINDOW_ICON_FILE = "assets/qtime_icon.ico"
LOGO_FILE = "assets/logo.png"

# ---------- Служебные строки ----------
RESPONSIBLE_PREFIX = "ответственное"   # строка-«стоп» в конце файла 1
DIALOG_OPEN_SOURCE = "Выберите файл «Отработанное время за месяц»"
DIALOG_SAVE_TARGET = "Сохранить УРВ"
DIALOG_DEFAULT_FILENAME = "УРВ.xlsx"
EXCEL_FILETYPES = (
    ("Excel (*.xlsx, *.xlsm)", "*.xlsx *.xlsm"),
    ("Все файлы", "*.*"),
)
EXCEL_FILETYPES_SAVE = (("Excel", "*.xlsx"),)

# ---------- Текстовые метки ----------
HEADER_FIO = "ФИО"
HEADER_INCOME = "приход"
HEADER_OUTCOME = "уход"
HEADER_TOTAL = "итого"

NO_INCOME = "нет входа"
NO_OUTCOME = "нет выхода"
ABSENT = "ОТСУТСТВОВАЛ"

# ---------- Разбор ячейки ----------
SEPARATOR_RE = r"-{3,}"     # строка вида ------
EMPTY_MARKS = ("-", "?", "", "—")  # что считаем пустым

# ---------- Определение «приход/уход» по одному времени ----------
NOON_HOUR = 13              # граница: до 13:00 — приход, иначе уход

# ---------- Даты ----------
DATE_FORMAT_OUT = "%d.%m.%Y"
DEFAULT_YEAR_MIN = 2020
DEFAULT_YEAR_MAX = 2100
DEFAULT_MONTH_MIN = 1
DEFAULT_MONTH_MAX = 12
DEFAULT_DAY_MIN = 1
DEFAULT_DAY_MAX = 31
DAYS_IN_WEEK = 7

# ---------- Выходные ----------
# В Файле 1 шапка имеет вид: 28 пн, 29 вт, 30 ср, 1 чт, 2 пт, 3 сб, 4 вс
# Колонки сб и вс — индексы внутри недельного блока (0-based).
WEEKEND_INDEXES = (5, 6)    # сб, вс

# ---------- Оформление Excel ----------
BORDER_COLOR = "999999"
HEADER_FILL_COLOR = "DCE6F1"
COL_WIDTH_FIO = 16
COL_WIDTH_TIME = 12
COL_WIDTH_TOTAL = 10
COL_WIDTH_STATUS = 24
COL_WIDTH_NORM = 10


# ---------- Пределы периода ----------
MAX_DAYS = 31               # максимум дней в таблице

# ---------- Границы интерфейса ----------
TREE_BORDER_COLOR = "#888888"
TREE_ROW_HEIGHT = 24
STATUS_FG_ACTIVE = "black"
STATUS_FG_OK = "green"
STATUS_FG_IDLE = "gray"

# ---------- Контрастная палитра сотрудников ----------
# Чередуем насыщенные и светлые оттенки, чтобы соседние блоки
# визуально не сливались.
PERSON_COLORS = (
    "#FFD9B3",   # 1  тёплый персиковый
    "#B3E0FF",   # 2  голубой
    "#FFC2C2",   # 3  розовый
    "#C2F0C2",   # 4  зелёный
    "#E6CCFF",   # 5  лавандовый
    "#FFE680",   # 6  жёлтый
    "#B3F0E6",   # 7  бирюзовый
    "#FFCC99",   # 8  оранжевый
    "#CCE0FF",   # 9  светло-синий
    "#E6FFB3",   # 10 салатовый
    "#FFB3D9",   # 11 малиновый
    "#D9D9D9",   # 12 серый
)

# оттенки
GEN_SATURATION = 0.55
GEN_LIGHTNESS = 0.82
GEN_HUE_STEP = 0.61803398875

# Насколько затемнять цвет шапки блока сотрудника (0..1).
HEADER_TINT_FACTOR = 0.78

# Цвет строки-разделителя между сотрудниками.
SEPARATOR_ROW_COLOR = "#3C3C3C"

# ---------- Размеры разделителя ----------
SEPARATOR_ROW_HEIGHT = 4


# ---------- Поиск шапки в Файле 1 ----------
# Маркер строки-заголовка. По нему находим:
#   • строку с датами (шапка),
#   • строку начала данных (шапка + 1),
#   • колонку ФИО,
#   • первую колонку с датами.
HEADER_MARKER = "фамилия"

# Сколько первых строк сканируем в поисках шапки.
HEADER_SEARCH_LIMIT = 30

# Сколько первых колонок сканируем в поисках маркера.
HEADER_COLUMN_LIMIT = 10


# ---------- Тексты ошибок для пользователя ----------
ERR_FILE_BUSY = (
    "Файл открыт в другой программе (например, Excel).\n"
    "Закройте его и повторите попытку."
)
ERR_FILE_NOT_FOUND = (
    "Файл не найден. Возможно, он был перемещён или удалён."
)
ERR_FILE_ACCESS = (
    "Нет доступа к файлу. Проверьте права или закройте его "
    "в других программах."
)
ERR_FILE_CORRUPT = (
    "Не удалось прочитать файл. Возможно, он повреждён "
    "или это не Excel-файл."
)
ERR_HEADER_NOT_FOUND = (
    "В файле не найдена строка с заголовком «Фамилия».\n"
    "Проверьте, что это тот самый файл «Отработанное время»."
)
ERR_SAVE_FAILED = (
    "Не удалось сохранить файл. Возможно, он открыт в Excel "
    "или нет прав на запись."
)
ERR_UNKNOWN = "Произошла непредвиденная ошибка.\n\n{details}"
ERR_OLD_FORMAT = (
    "Файл в устаревшем формате .xls.\n"
    "Программа работает с современным форматом .xlsx.\n\n"
    "Откройте файл в Excel и сохраните как «Книга Excel (*.xlsx)», "
    "затем повторите попытку."
)

# ---------- Errno (для OSError) ----------
ERRNO_PERMISSION_DENIED = 13
ERRNO_FILE_NOT_FOUND = 2

# ---------- Маркеры ValueError для распознавания ошибок ----------
VALUE_ERROR_HEADER_MARKERS = ("шапка", "маркер", "фамилия")


# ---------- Графики и нормы ----------
WORK_HOURS_OPTIONS = (9, 12)
DEFAULT_WORK_HOURS = 9
DEFAULT_START_TIME = "09:00"

SCHEDULE_CHECK_LABEL = "Учитывать график и опоздания"
SCHEDULE_DIALOG_TITLE = "Настройки графиков"
SCHEDULE_DIALOG_APPLY = "Применить"
SCHEDULE_DIALOG_CANCEL = "Отмена"

# ---------- Статусы дня ----------
STATUS_OK = "ОК"
STATUS_LATE = "опоздание"
STATUS_INCOMPLETE = "не полная смена"

# ---------- Цвета статусов (приоритет сверху вниз) ----------
# Строка красится в цвет самого «тревожного» статуса.
STATUS_PRIORITY = (
    STATUS_LATE,        # 1 — красный
    STATUS_INCOMPLETE,  # 2 — оранжевый
    STATUS_OK,          # 3 — зелёный
)

STATUS_COLORS = {
    STATUS_LATE: "#FFC2C2",        # красный
    STATUS_INCOMPLETE: "#FFE0B3",  # оранжевый
    STATUS_OK: "#C2F0C2",          # зелёный
}

# Цвет текста в статусных колонках Excel (жирный шрифт статуса).
STATUS_TEXT_COLORS = {
    STATUS_LATE: "C00000",         # тёмно-красный
    STATUS_INCOMPLETE: "C07000",   # тёмно-оранжевый
    STATUS_OK: "006000",           # тёмно-зелёный
}

# ---------- Колонки в Файле 2 (1-based) ----------
OUT_COL_DATE = 1
OUT_COL_INCOME = 2
OUT_COL_OUTCOME = 3
OUT_COL_TOTAL = 4
OUT_COL_STATUS_1 = 5
OUT_COL_STATUS_2 = 6
OUT_COL_NORM = 7
OUT_COL_COUNT = 7
OUT_HEADER_NORM = "норма"


# ---------- Заголовки диалогов ----------
DLG_TITLE_WARNING = "Внимание"
DLG_TITLE_ERROR_READ = "Ошибка чтения"
DLG_TITLE_ERROR_SAVE = "Ошибка сохранения"
DLG_TITLE_ERROR_DATE = "Ошибка"
DLG_TITLE_DONE = "Готово"

# ---------- Тексты сообщений ----------
MSG_OPEN_SOURCE_FIRST = "Сначала откройте Файл 1"
MSG_PROCESS_FIRST = "Сначала нажмите «Обработать»"
MSG_INVALID_START_DATE = "Некорректная дата начала недели"
MSG_SAVED = "Сохранено:\n{path}"
MSG_CANCELLED = "Отменено"
MSG_SOURCE_SELECTED = "Выбран: {name}"
MSG_PROCESSED = "Обработано: {count} чел., с {date}"
MSG_FILE_NOT_SELECTED = "Файл не выбран"

# ---------- Размеры и отступы интерфейса ----------
DATE_ENTRY_WIDTH = 12
SPINBOX_YEAR_WIDTH = 6
SPINBOX_MONTH_WIDTH = 4
SPINBOX_DAY_WIDTH = 4

PAD_XS = 4
PAD_S = 8
PAD_M = 12
PAD_L = 20
PANEL_PADDING = 8

# ---------- Стиль Treeview ----------
TREE_SELECTED_BG = "#4A90D9"
TREE_SELECTED_FG = "white"
