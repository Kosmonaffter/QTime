"""
Проверка версии приложения на GitHub.

Скачивает docs/version.json и сравнивает с APP_VERSION.
Не скачивает обновление — только сообщает о наличии новой версии.
"""

import json
from typing import Optional

import requests

from core.constants import (
    APP_VERSION,
    VERSION_CHECK_TIMEOUT,
    VERSION_CHECK_URL,
)


def parse_version(text: str):
    """'v1.3.0' или '1.3.0' → (1, 3, 0). Пустой кортеж при ошибке."""
    if not text:
        return ()
    cleaned = str(text).strip().lstrip("vV")
    try:
        return tuple(int(p) for p in cleaned.split("."))
    except ValueError:
        return ()


def is_newer(latest: str, current: str) -> bool:
    """Проверяет, что latest > current."""
    latest_t = parse_version(latest)
    current_t = parse_version(current)
    if not latest_t or not current_t:
        return False
    return latest_t > current_t


def fetch_version_info() -> Optional[dict]:
    """
    Скачивает version.json.

    Возвращает dict или None при ошибке (нет сети, таймаут, битый JSON).
    """
    try:
        response = requests.get(
            VERSION_CHECK_URL,
            timeout=VERSION_CHECK_TIMEOUT,
            headers={"User-Agent": "QTime-Version-Check"},
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def check_for_update():
    """
    Проверяет наличие новой версии.

    Возвращает (has_update: bool, latest_version: str | None).
    """
    info = fetch_version_info()
    if not info:
        return False, None
    latest = info.get("version", "")
    if not latest:
        return False, None
    if is_newer(latest, APP_VERSION):
        return True, latest
    return False, None