<div align="center">

# QTime

**Десктопное приложение для учёта рабочего времени и формирования УРВ**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## Содержание

- [О проекте](#о-проекте)
- [Возможности](#возможности)
- [Скриншоты](#скриншоты)
- [Установка](#установка)
- [Запуск](#запуск)
- [Сборка EXE](#сборка-exe)
- [Структура проекта](#структура-проекта)
- [Как это работает](#как-это-работает)
- [Формат данных](#формат-данных)
- [О программе](#о-программе)
- [Лицензия](#лицензия)

<p align="right"><a href="#содержание">↑ к содержанию</a></p>

---

## О проекте

**QTime** — утилита для еженедельной обработки табеля рабочего времени.
Берёт «сырой» Excel-файл с отметками СКУД и формирует готовый **УРВ**
(учёт рабочего времени) с расчётом отработанных часов по каждому
сотруднику.

Приложение рассчитано на бухгалтеров, кадровиков и руководителей,
которые каждый понедельник вручную переносят данные за прошлую неделю.

<p align="right"><a href="#содержание">↑ к содержанию</a></p>

---

## Возможности

- Импорт Excel-файла «Отработанное время за месяц».
- Выбор даты начала недели: **интерактивный календарь** или ручные поля.
- Автоматический расчёт отработанного времени (`приход` → `уход`).
- Поддержка неполных смен:
  - одно время до 13:00 → `приход`, `уход = нет выхода`;
  - одно время после 13:00 → `уход`, `приход = нет входа`;
  - нет обоих → `ОТСУТСТВОВАЛ`.
- Пустые сб/вс **не попадают** в итоговый файл.
- Период чтения — до **31 дня**.
- Каждый сотрудник получает **уникальный цвет**, сохраняемый в Excel.
- Экспорт в новый `.xlsx` с границами и заливкой.
- Встроенные окна «О программе» и «Инструкция».

<p align="right"><a href="#содержание">↑ к содержанию</a></p>

---

## Скриншоты

```
docs/screenshot-main.png
docs/screenshot-calendar.png
docs/screenshot-result.png

```

<p align="right"><a href="#содержание">↑ к содержанию</a></p>

---

## Установка

### Требования

- Python 3.10+
- Windows 10/11

### Шаги

```bash
git clone https://github.com/Kosmonaffter/QTime.git
cd QTime
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt`:

```
openpyxl>=3.1.0
tkcalendar>=1.6.1
```

<p align="right"><a href="#содержание">↑ к содержанию</a></p>

---

## Запуск

```bash
python main.py
```

<p align="right"><a href="#содержание">↑ к содержанию</a></p>

---

## Сборка EXE

### Установка PyInstaller

```bash
pip install pyinstaller
```

### Сборка одной командой

```bash
pyinstaller --noconfirm --clean --windowed ^
  --name QTime ^
  --icon assets/icon.ico ^
  --add-data "assets;assets" ^
  main.py
```

Готовый файл: `dist/QTime/QTime.exe`.

### Или через `QTime.spec`

```bash
pyinstaller --noconfirm --clean QTime.spec
```

### `build.bat`

```bat
@echo off
chcp 65001 > nul
echo === Сборка QTime ===
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --noconfirm --clean QTime.spec
echo === Готово: dist\QTime\QTime.exe ===
pause
```

<p align="right"><a href="#содержание">↑ к содержанию</a></p>

---

## Структура проекта

```
QTime/
├── main.py
├── requirements.txt
├── QTime.spec
├── build.bat
├── README.md
├── LICENSE
├── .gitignore
├── assets/
│   └── icon.ico
├── core/
│   ├── __init__.py
│   ├── constants.py
│   ├── color_utils.py
│   ├── time_utils.py
│   ├── source_reader.py
│   └── target_writer.py
└── ui/
    ├── __init__.py
    ├── app_window.py
    ├── about_dialog.py
    └── help_dialog.py
```

<p align="right"><a href="#содержание">↑ к содержанию</a></p>

---

## Как это работает

1. Открываем **Файл 1** — «Отработанное время за месяц».
2. Указываем **дату начала недели** (календарь или ручные поля).
3. Нажимаем **«Обработать»** — данные попадают в таблицу предпросмотра.
4. Нажимаем **«Сохранить УРВ»** — получаем новый Excel-файл.

### Логика разбора ячейки

```
08:58    ← приход
19:00    ← уход
------
8:00     ← игнорируется
```

Если в ячейке одно время:
```
| Ситуация      | Приход         | Уход         |
|---------------|----------------|--------------|
| время < 13:00 | `HH:MM`        | `нет выхода` |
| время ≥ 13:00 | `нет входа`    | `HH:MM`      |
| нет обоих     | `ОТСУТСТВОВАЛ` | —            |
```
<p align="right"><a href="#содержание">↑ к содержанию</a></p>

---

## Формат данных

### Файл 1 — «Отработанное время за месяц»
```
| A | B | C | D | E | ... |
|---|--------------------|---------------|---------------|-------|-----|
| № | Фамилия, инициалы  | 28 пн         | 29 вт         | 30 ср | ... |
| 1 | Гайдукевич Людмила | 08:58 / 19:00 | 08:56 / 19:24 | ...   | ... |
```
### Файл 2 — УРВ (результат)
```
| A          | B      | C     | D     |
|------------|--------|-------|-------|
| ФИО        | приход | уход  | итого |
| 28.09.2026 | 08:58  | 19:00 | 10:02 |
| 29.09.2026 | 08:56  | 19:24 | 10:28 |
```
<p align="right"><a href="#содержание">↑ к содержанию</a></p>

---

## О программе

**QTime** — внутренний инструмент для автоматизации еженедельного
формирования УРВ.

### Технический стек
```
- Python 3.10+
- Tkinter + tkcalendar
- openpyxl
- PyInstaller (сборка EXE)
```
### Разработчик
```
- **ФИО:** Atlasyuk Uriy Sergeevich
- **GitHub:** [Kosmonaffter](https://github.com/Kosmonaffter)
- **Email:** kosmonaffter@yandex.ru
- **Телефон:** +7 (926) 375-25-67
- **Telegram:** `kosmonafftsb`
- **Instagram:** `kosmonaffter`
```
© 2026 KosmonafftTechnologies. Все права защищены.

<p align="right"><a href="#содержание">↑ к содержанию</a></p>

---

## Лицензия

MIT. См. [LICENSE](LICENSE).

<p align="right"><a href="#содержание">↑ к содержанию</a></p>