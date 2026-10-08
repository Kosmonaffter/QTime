"""
Графики работы и оценка дня.

Считает опоздание, неполную смену и итоговый статус дня
на основе начала смены и её длительности.
"""

from dataclasses import dataclass

from core.constants import (
    NO_INCOME,
    NO_OUTCOME,
    STATUS_INCOMPLETE,
    STATUS_LATE,
    STATUS_OK,
)
from core.time_utils import parse_time


MINUTES_IN_HOUR = 60


@dataclass
class Schedule:
    """Настройки графика одного сотрудника."""

    start_time: str    # '09:00'
    hours: int         # 9 или 12

    def start_minutes(self) -> int:
        """Возвращает начало смены в минутах от полуночи."""
        parsed = parse_time(self.start_time)
        if not parsed:
            return 0
        return parsed[0] * MINUTES_IN_HOUR + parsed[1]

    def norm_minutes(self) -> int:
        """Возвращает норму смены в минутах."""
        return self.hours * MINUTES_IN_HOUR


@dataclass
class DayEvaluation:
    """Результат оценки одного дня."""

    status_late: str        # 'опоздание +0:15' или ''
    status_incomplete: str  # 'не полная смена −0:30' или ''
    priority_status: str    # что использовать для цвета строки
    norm_text: str          # '9:00' или '12:00'


def evaluate_day(income, outcome, total, schedule):
    """
    Оценивает день по графику.

    Возвращает DayEvaluation. Если данных нет — все поля пустые.
    """
    norm_text = _format_norm(schedule.hours)

    if not _has_full_data(income, outcome, total):
        return DayEvaluation("", "", "", norm_text)

    start_minutes = schedule.start_minutes()
    norm_minutes = schedule.norm_minutes()

    income_minutes = _to_minutes(income)
    total_minutes = _to_minutes(total)

    status_late = _check_late(income_minutes, start_minutes)
    status_incomplete = _check_incomplete(total_minutes, norm_minutes)

    priority = _pick_priority(status_late, status_incomplete)

    return DayEvaluation(
        status_late=status_late,
        status_incomplete=status_incomplete,
        priority_status=priority,
        norm_text=norm_text,
    )


def _has_full_data(income, outcome, total) -> bool:
    """Проверяет, что есть все данные для оценки дня."""
    if not income or not outcome or not total:
        return False
    if income in (NO_INCOME,) or outcome in (NO_OUTCOME,):
        return False
    return True


def _to_minutes(value: str) -> int:
    """'09:30' -> 570."""
    parsed = parse_time(value)
    if not parsed:
        return 0
    return parsed[0] * MINUTES_IN_HOUR + parsed[1]


def _check_late(income_minutes: int, start_minutes: int) -> str:
    """
    Проверяет опоздание.

    Приход > начала смены — опоздание. Иначе — пусто.
    """
    if income_minutes <= start_minutes:
        return ""
    diff = income_minutes - start_minutes
    return f"{STATUS_LATE} +{_format_diff(diff)}"


def _check_incomplete(total_minutes: int, norm_minutes: int) -> str:
    """
    Проверяет неполную смену.

    Итого < нормы — неполная. Иначе — пусто.
    """
    if total_minutes >= norm_minutes:
        return ""
    diff = norm_minutes - total_minutes
    return f"{STATUS_INCOMPLETE} \u2212{_format_diff(diff)}"


def _pick_priority(status_late: str, status_incomplete: str) -> str:
    """
    Выбирает статус для окраски строки.

    Приоритет: опоздание > неполная > ОК.
    """
    if status_late:
        return STATUS_LATE
    if status_incomplete:
        return STATUS_INCOMPLETE
    return STATUS_OK


def _format_diff(minutes: int) -> str:
    """15 -> '0:15', 90 -> '1:30'."""
    hours, mins = divmod(minutes, MINUTES_IN_HOUR)
    return f"{hours}:{mins:02d}"


def _format_norm(hours: int) -> str:
    """9 -> '9:00', 12 -> '12:00'."""
    return f"{hours}:00"


def empty_evaluation():
    """Пустая оценка — для дней без графика."""
    return DayEvaluation("", "", "", "")