"""
Сверка данных Болида и Табель.

Сопоставляет сотрудников по ФИО, считает факт и проставленные
часы, определяет статус каждого дня и итога по месяцу.
"""

import calendar
from datetime import date

from core.sk.constants import (
    GRAPH_MAIN,
    GRAPH_MAIN_HOURS,
    GRAPH_WAREHOUSE_PREFIX,
    GRAPH_WAREHOUSE_HOURS,
    LUNCH_HOURS,
    MINUTES_IN_HOUR,
    NO_DATA_IN_BOLID,
    NO_DATA_IN_ZUP,
    NO_INCOME,
    NO_OUTCOME,
    STATUS_GRAY,
    STATUS_GREEN,
    STATUS_ORANGE,
    STATUS_RED,
    STATUS_YELLOW,
    TOTAL_TOLERANCE_HOURS,
)


def compare(bolid_people, zup_people, month: int, year: int):
    """
    Сверяет данные Болида и Табель.

    Возвращает список сотрудников с готовыми днями и итогами.
    Сотрудники без данных в одном из источников — тоже попадают
    в список с пометкой.
    """
    bolid_index = _index_by_fio(bolid_people)
    zup_index = _index_by_fio(zup_people)

    all_fio = _merge_keys(bolid_index, zup_index)
    result = []

    for fio in all_fio:
        person = _build_person(
            fio, bolid_index.get(fio), zup_index.get(fio), month, year,
        )
        result.append(person)

    return result


# ---------- Индексация ----------

def _index_by_fio(people):
    """Строит {fio_norm: person}."""
    return {_normalize(p["fio"]): p for p in people}


def _merge_keys(first: dict, second: dict):
    """Объединяет ключи обоих словарей, сохраняя порядок."""
    keys = list(first.keys())
    for key in second:
        if key not in keys:
            keys.append(key)
    return keys


def _normalize(fio: str) -> str:
    """
    Нормализует ФИО: нижний регистр, ё → е, лишние пробелы убираем.
    """
    text = fio.lower().replace("ё", "е")
    return " ".join(text.split())


# ---------- Построение записи по сотруднику ----------

def _build_person(fio_key, bolid, zup, month, year):
    """Строит запись одного сотрудника с днями и итогами."""
    graph = zup["graph"] if zup else ""
    norm_hours = _norm_for_graph(graph)

    days = _build_days(bolid, zup, month, year, norm_hours)
    total_fact = _sum_fact(days)
    total_zup = _sum_zup(days)

    return {
        "fio": _display_fio(bolid, zup),
        "graph": graph,
        "norm_hours": norm_hours,
        "days": days,
        "total_fact": round(total_fact, 2),
        "total_zup": round(total_zup, 2),
        "total_ok": _is_total_ok(total_fact, total_zup),
        "no_bolid": bolid is None,
        "no_zup": zup is None,
    }


def _display_fio(bolid, zup):
    """Возвращает 'Фамилия Имя' из любого источника."""
    if bolid:
        return bolid["fio"]
    if zup:
        return zup["fio"]
    return ""


def _norm_for_graph(graph: str) -> int:
    """
    Возвращает норму часов по графику.

    Основной график — 9 часов.
    Склад X смена — 12 часов.
    """
    if not graph:
        return 0
    if graph.startswith(GRAPH_WAREHOUSE_PREFIX):
        return GRAPH_WAREHOUSE_HOURS
    if graph == GRAPH_MAIN:
        return GRAPH_MAIN_HOURS
    return 0


# ---------- Дни ----------

def _build_days(bolid, zup, month, year, norm_hours):
    """Строит список дней по реальному числу дней месяца."""
    total_days = calendar.monthrange(year, month)[1]
    days = []
    for day in range(1, total_days + 1):
        record = _build_day(
            day, month, year, bolid, zup, norm_hours,
        )
        days.append(record)
    return days


def _build_day(day, month, year, bolid, zup, norm_hours):
    """Строит запись одного дня."""
    bolid_day = _bolid_day(bolid, day, month, year)
    zup_hours = zup["days"].get(day) if zup else None

    income = bolid_day["income"] if bolid_day else None
    outcome = bolid_day["outcome"] if bolid_day else None
    fact_hours = _fact_hours(income, outcome)

    day_date = _safe_date(year, month, day)
    status = _day_status(
        bolid=bolid_day, zup_hours=zup_hours, fact_hours=fact_hours,
    )
    diff_minutes = _diff_minutes(fact_hours, zup_hours, status)

    return {
        "day": day,
        "date": day_date,
        "income": income or "",
        "outcome": outcome or "",
        "fact_hours": fact_hours,
        "fact_text": _format_hours_text(fact_hours),
        "zup": zup_hours,
        "diff_minutes": diff_minutes,
        "diff_text": _format_diff(diff_minutes),
        "status": status,
        "no_income": bolid_day is not None and not income,
        "no_outcome": bolid_day is not None and not outcome,
    }


def _bolid_day(bolid, day, month, year):
    """Возвращает запись дня из Болида или None."""
    if not bolid:
        return None
    target = _safe_date(year, month, day)
    if target is None:
        return None
    return bolid["days"].get(target)


def _safe_date(year: int, month: int, day: int):
    """date(year, month, day) или None для некорректных дат."""
    try:
        return date(year, month, day)
    except ValueError:
        return None


# ---------- Расчёты ----------

def _fact_hours(income, outcome):
    """Возвращает часы между приходом и уходом или None."""
    if not income or not outcome:
        return None
    start = _time_to_minutes(income)
    end = _time_to_minutes(outcome)
    if start is None or end is None:
        return None
    diff = end - start
    if diff < 0:
        diff += 24 * MINUTES_IN_HOUR
    return diff / MINUTES_IN_HOUR


def _time_to_minutes(value: str):
    """'06:23:04' -> 383 минут. Или None."""
    parts = value.split(":")
    if len(parts) < 2:
        return None
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
    except ValueError:
        return None
    return hours * MINUTES_IN_HOUR + minutes


def _day_status(bolid, zup_hours, fact_hours):
    """
    Определяет статус дня.

    green  — Табель + 1 == Факт;
    red    — недоработка (факт < норма);
    orange — переработка (факт > норма);
    yellow — есть в Болиде, нет Табеле;
    gray   — нет нигде.
    """
    if bolid is None or zup_hours is None:
        return STATUS_YELLOW if bolid is not None else STATUS_GRAY
    if fact_hours is None:
        return STATUS_YELLOW

    expected = zup_hours + LUNCH_HOURS
    diff = fact_hours - expected

    if abs(diff) < 1 / MINUTES_IN_HOUR:
        return STATUS_GREEN
    if diff < 0:
        return STATUS_RED
    return STATUS_ORANGE


def _diff_minutes(fact_hours, zup_hours, status):
    """
    Считает расхождение в минутах.

    Факт − (Табель + обед). Переработка — плюс, недоработка — минус.
    """
    if status not in (STATUS_GREEN, STATUS_RED):
        return None
    if fact_hours is None or zup_hours is None:
        return None
    expected = zup_hours + LUNCH_HOURS
    return round((fact_hours - expected) * MINUTES_IN_HOUR)


def _sum_fact(days):
    """Сумма факта по дням (в десятичных часах)."""
    return sum(d["fact_hours"] for d in days if d["fact_hours"])


def _sum_zup(days):
    """Сумма Табель по дням."""
    return sum(d["zup"] for d in days if d["zup"])


def _is_total_ok(fact: float, zup: float) -> bool:
    """Итог ОК, если разница ≤ допуска."""
    return abs(fact - zup) <= TOTAL_TOLERANCE_HOURS


# ---------- Форматирование ----------

def _format_hours_text(hours):
    """12.7 -> '12 ч 42 м'. None -> ''."""
    if hours is None:
        return ""
    total_minutes = round(hours * MINUTES_IN_HOUR)
    h, m = divmod(total_minutes, MINUTES_IN_HOUR)
    return f"{h} ч {m:02d} м"


def _format_diff(minutes):
    """35 -> '+00:35'. -35 -> '−00:35'. None -> ''."""
    if minutes is None:
        return ""
    sign = "+" if minutes >= 0 else "\u2212"
    total = abs(minutes)
    h, m = divmod(total, MINUTES_IN_HOUR)
    return f"{sign}{h:02d}:{m:02d}"
