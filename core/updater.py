"""
Проверка и установка обновлений QTime.

Скачивает version.json с GitHub, сравнивает с APP_VERSION,
при необходимости скачивает новый .exe и запускает .bat для замены.
"""

import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional

from core.constants import (
    APP_VERSION,
    UPDATE_CHECK_DELAY_MS,
    UPDATE_EXE_NAME,
    UPDATE_SCRIPT_EXT,
    UPDATE_SCRIPT_PREFIX,
    UPDATE_TIMEOUT_SECONDS,
    UPDATE_TMP_PREFIX,
    UPDATE_URL,
)


def parse_version(text: str):
    """
    'v1.3.0' или '1.3.0' → (1, 3, 0).

    Возвращает () при ошибке.
    """
    cleaned = text.strip().lstrip("vV")
    parts = cleaned.split(".")
    try:
        return tuple(int(p) for p in parts)
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
    Скачивает version.json с GitHub.

    Возвращает dict или None при любой ошибке (нет сети, парсинг).
    """
    import json

    try:
        request = urllib.request.Request(
            UPDATE_URL,
            headers={"User-Agent": "QTime-Updater"},
        )
        with urllib.request.urlopen(
            request, timeout=UPDATE_TIMEOUT_SECONDS
        ) as response:
            data = response.read().decode("utf-8")
        return json.loads(data)
    except Exception:
        return None


def check_for_update():
    """
    Проверяет наличие новой версии.

    Возвращает (has_update: bool, info: dict | None).
    info — словарь с полями version, download_url, release_notes.
    """
    info = fetch_version_info()
    if info is None:
        return False, None

    latest = info.get("version", "")
    if not latest:
        return False, None

    if not is_newer(latest, APP_VERSION):
        return False, info

    return True, info


# ---------- Установка ----------

def is_frozen() -> bool:
    """Работает ли приложение как .exe (PyInstaller)."""
    return getattr(sys, "frozen", False)


def current_exe_path() -> Optional[Path]:
    """Путь к текущему .exe или None (если запущен как .py)."""
    if not is_frozen():
        return None
    return Path(sys.executable).resolve()


def can_install_update() -> bool:
    """
    Можно ли заменить текущий .exe.

    Проверяем, что приложение запущено как .exe и рядом можно писать.
    """
    exe_path = current_exe_path()
    if exe_path is None:
        return False
    if not exe_path.exists():
        return False
    try:
        test_file = exe_path.parent / ".qtime_write_test"
        test_file.write_text("test", encoding="utf-8")
        test_file.unlink()
        return True
    except Exception:
        return False


def download_and_install(download_url: str) -> str:
    """
    Скачивает новый .exe и запускает .bat для замены.

    Возвращает путь к .bat или бросает исключение.
    """
    exe_path = current_exe_path()
    if exe_path is None:
        raise RuntimeError("Приложение запущено не как .exe")

    tmp_dir = Path(tempfile.gettempdir())
    tmp_exe = tmp_dir / f"{UPDATE_TMP_PREFIX}{UPDATE_EXE_NAME}"

    _download_file(download_url, tmp_exe)

    script_path = tmp_dir / f"{UPDATE_SCRIPT_PREFIX}install{UPDATE_SCRIPT_EXT}"
    _write_script(script_path, tmp_exe, exe_path)

    subprocess.Popen(
        ["cmd", "/c", str(script_path)],
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    return str(script_path)


def _download_file(url: str, target: Path):
    """Скачивает файл по URL в target."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "QTime-Updater"},
    )
    with urllib.request.urlopen(
        request, timeout=UPDATE_TIMEOUT_SECONDS
    ) as response:
        data = response.read()
    target.write_bytes(data)


def _write_script(script_path: Path, new_exe: Path, old_exe: Path):
    """
    Пишет .bat-скрипт, который:
    1. Ждёт завершения текущего процесса.
    2. Копирует новый .exe поверх старого.
    3. Запускает новый .exe.
    4. Удаляет временные файлы и себя.
    """
    pid = os.getpid()
    script = f"""@echo off
chcp 65001 > nul
echo Ожидание закрытия QTime...
:wait
tasklist /FI "PID eq {pid}" 2>NUL | find /I "{pid}" >NUL
if not errorlevel 1 (
    timeout /t 1 /nobreak > nul
    goto wait
)
echo Установка обновления...
move /Y "{new_exe}" "{old_exe}"
echo Запуск новой версии...
start "" "{old_exe}"
timeout /t 2 /nobreak > nul
del "%~f0"
"""
    script_path.write_text(script, encoding="cp866")


def restart_application():
    """Закрывает текущее приложение."""
    sys.exit(0)
