"""
Перевод технических ошибок в понятные пользователю сообщения.

Используется в UI, чтобы не показывать пользователю трейсбеки
и коды errno.
"""

from core.constants import (
    ERR_FILE_ACCESS,
    ERR_FILE_BUSY,
    ERR_FILE_CORRUPT,
    ERR_FILE_NOT_FOUND,
    ERR_HEADER_NOT_FOUND,
    ERR_NO_DATA,
    ERR_SAVE_FAILED,
    ERR_UNKNOWN,
)


def humanize_error(error: Exception) -> str:
    """
    Возвращает понятный текст ошибки для пользователя.

    Разбирает тип исключения и его текст, подбирает подходящее
    сообщение из констант.
    """
    if isinstance(error, PermissionError):
        return ERR_FILE_BUSY

    if isinstance(error, FileNotFoundError):
        return ERR_FILE_NOT_FOUND

    if isinstance(error, IsADirectoryError):
        return ERR_FILE_ACCESS

    if isinstance(error, OSError):
        return _humanize_os_error(error)

    if isinstance(error, ValueError):
        return _humanize_value_error(error)

    return ERR_UNKNOWN.format(details=str(error))


def _humanize_os_error(error: OSError) -> str:
    """
    Разбирает OSError по errno.

    Errno 13 — доступ запрещён (файл занят).
    Errno 2 — файл не найден.
    """
    errno = getattr(error, "errno", None)
    if errno == 13:
        return ERR_FILE_BUSY
    if errno == 2:
        return ERR_FILE_NOT_FOUND
    return ERR_FILE_ACCESS


def _humanize_value_error(error: ValueError) -> str:
    """
    Разбирает ValueError: у нас это чаще всего отсутствие шапки.
    """
    text = str(error).lower()
    if "шапка" in text or "маркер" in text or "фамилия" in text:
        return ERR_HEADER_NOT_FOUND
    return ERR_UNKNOWN.format(details=str(error))


def humanize_save_error(error: Exception) -> str:
    """
    Отдельный текст для ошибок сохранения.

    Сохранение чаще всего падает из-за занятого файла.
    """
    if isinstance(error, (PermissionError, OSError)):
        return ERR_SAVE_FAILED
    return ERR_UNKNOWN.format(details=str(error))
