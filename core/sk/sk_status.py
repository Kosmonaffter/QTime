"""
Форматирование данных СК для UI и Excel.

Одна точка правды для текстовых меток расхождений —
чтобы UI и Excel показывали одинаково.
"""

from core.sk.constants import MINUTES_IN_HOUR


def format_diff(minutes):
    """
    Минуты → 'HH:MM' со знаком.

    35 → '+00:35'
    -35 → '−00:35'
    None → ''
    """
    if minutes is None:
        return ""
    sign = "+" if minutes >= 0 else "\u2212"
    total = abs(minutes)
    hours, mins = divmod(total, MINUTES_IN_HOUR)
    return f"{sign}{hours:02d}:{mins:02d}"


def format_diff_hours(diff_hours: float) -> str:
    """
    Разница в часах (float) → 'HH:MM' со знаком.

    19.3 → '+19:18'
    -0.5 → '−00:30'
    """
    total_minutes = round(diff_hours * MINUTES_IN_HOUR)
    return format_diff(total_minutes)


def format_fact_total(value: float) -> str:
    """Факт в итоге: 184.80."""
    return f"{value:.2f}"


def format_zup_total(value: float) -> str:
    """ЗУП в итоге: 165.50."""
    return f"{value:.2f}"


def day_diff_text(day) -> str:
    """
    Текст колонки «Расхождение» для дня.

    Приоритет: расчёт → 'нет ЗУП'.
    """
    from core.sk.constants import NO_DATA_IN_ZUP, STATUS_YELLOW

    if day["diff_text"]:
        return day["diff_text"]
    if day["status"] == STATUS_YELLOW:
        if day["zup"] is None and (day["income"] or day["outcome"]):
            return NO_DATA_IN_ZUP
    return ""
