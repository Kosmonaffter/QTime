"""
Цвета для сотрудников.

Один и тот же цвет используется и в Tkinter, и в Excel,
чтобы блоки визуально совпадали.
"""

from core.constants import (
    HEADER_TINT_FACTOR,
    PERSON_COLORS,
)


def pick_color(index: int) -> str:
    """
    Возвращает HEX-цвет для сотрудника по его порядковому номеру.

    Если базовых цветов не хватило — генерирует новый оттенок.
    """
    if index < len(PERSON_COLORS):
        return PERSON_COLORS[index]
    return _generate_color(index - len(PERSON_COLORS))


def _generate_color(seed: int) -> str:
    """
    Генерирует пастельный HEX-цвет по числовому seed.

    Формула даёт предсказуемый, но разнообразный результат.
    """
    red = 200 + (seed * 37) % 56
    green = 200 + (seed * 53) % 56
    blue = 200 + (seed * 71) % 56
    return f"#{red:02X}{green:02X}{blue:02X}"


def header_color(base_color: str) -> str:
    """
    Затемняет базовый цвет — для шапки блока сотрудника.

    Работает и с Tkinter, и с Excel (один и тот же HEX).
    """
    red, green, blue = _hex_to_rgb(base_color)
    red = int(red * HEADER_TINT_FACTOR)
    green = int(green * HEADER_TINT_FACTOR)
    blue = int(blue * HEADER_TINT_FACTOR)
    return f"#{red:02X}{green:02X}{blue:02X}"


def _hex_to_rgb(color: str):
    """'#FFE4B5' -> (255, 228, 181)."""
    color = color.lstrip("#")
    return (
        int(color[0:2], 16),
        int(color[2:4], 16),
        int(color[4:6], 16),
    )


def to_excel_color(color: str) -> str:
    """
    Tkinter-HEX '#FFE4B5' -> Excel-HEX 'FFE4B5'.

    Excel не понимает решётку.
    """
    return color.lstrip("#")