"""
Утилиты для доступа к ресурсам приложения.

Работает и в исходниках, и в .exe (PyInstaller).
"""

import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    """
    Возвращает абсолютный путь к ресурсу.

    В .exe PyInstaller распаковывает данные во временную папку
    _MEIPASS — там и ищем. В исходниках — от корня проекта.
    """
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base) / relative
    return Path(__file__).resolve().parent.parent / relative
