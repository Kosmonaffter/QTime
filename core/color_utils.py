"""
Цвета для сотрудников.

Один и тот же цвет используется и в Tkinter, и в Excel,
чтобы блоки визуально совпадали.

Если сотрудников больше, чем базовых цветов, — генерируем оттенки
с равномерным шагом по HSL. Это даёт предсказуемо контрастные
соседние цвета.
"""

import colorsys

from core.constants import (
    GEN_SATURATION,
    GEN_LIGHTNESS,
    GEN_HUE_STEP,
    HEADER_TINT_FACTOR,
    PERSON_COLORS,
)


def pick_color(index: int) -> str:
    """
    Возвращает HEX-цвет для сотрудника по его порядковому номеру.

    Если базовых цветов не хватило — генерирует новый оттенок
    с равномерным шагом по кругу оттенков.
    """
    if index < len(PERSON_COLORS):
        return PERSON_COLORS[index]
    return _generate_color(index - len(PERSON_COLORS))


def _generate_color(seed: int) -> str:
    """
    Генерирует контрастный пастельный HEX-цвет по числовому seed.

    Использует HSL: тон шагает по кругу золотым сечением,
    насыщенность и яркость фиксированы.
    """
    hue = (seed * GEN_HUE_STEP) % 1.0
    red, green, blue = colorsys.hls_to_rgb(
        hue, GEN_LIGHTNESS, GEN_SATURATION
    )
    return _rgb_to_hex(red, green, blue)


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


def to_excel_color(color: str) -> str:
    """
    Tkinter-HEX '#FFE4B5' -> Excel-HEX 'FFE4B5'.

    Excel не понимает решётку.
    """
    return color.lstrip("#")


def _hex_to_rgb(color: str):
    """'#FFE4B5' -> (255, 228, 181)."""
    color = color.lstrip("#")
    return (
        int(color[0:2], 16),
        int(color[2:4], 16),
        int(color[4:6], 16),
    )


def _rgb_to_hex(red: float, green: float, blue: float) -> str:
    """(0.5, 0.5, 0.5) -> '#808080'."""
    r = int(round(red * 255))
    g = int(round(green * 255))
    b = int(round(blue * 255))
    return f"#{r:02X}{g:02X}{b:02X}"
