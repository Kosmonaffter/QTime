"""
Перевод технических ошибок в понятные пользователю сообщения.

Используется в UI, чтобы не показывать пользователю трейсбеки
и коды errno.
"""

from zipfile import BadZipFile
from openpyxl.utils.exceptions import InvalidFileException

from core.constants import (
    ERR_FILE_ACCESS,
    ERR_FILE_BUSY,
    ERR_FILE_CORRUPT,
    ERR_FILE_NOT_FOUND,
    ERR_HEADER_NOT_FOUND,
    ERR_OLD_FORMAT,
    ERR_SAVE_FAILED,
    ERR_UNKNOWN,
    ERRNO_FILE_NOT_FOUND,
    ERRNO_PERMISSION_DENIED,
    VALUE_ERROR_HEADER_MARKERS,
)


def humanize_error(error: Exception) -> str:
    """
    Возвращает понятный текст ошибки для пользователя.

    Разбирает тип исключения и его текст, подбирает подходящее
    сообщение из констант.
    """
    if isinstance(error, InvalidFileException):
        return ERR_OLD_FORMAT

    if isinstance(error, BadZipFile):
        return ERR_FILE_CORRUPT

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
    if error.errno == ERRNO_PERMISSION_DENIED:
        return ERR_FILE_BUSY
    if error.errno == ERRNO_FILE_NOT_FOUND:
        return ERR_FILE_NOT_FOUND
    return ERR_FILE_ACCESS


def _humanize_value_error(error: ValueError) -> str:
    """
    Разбирает ValueError: у нас это чаще всего отсутствие шапки.
    """
    text = str(error).lower()
    if any(m in text for m in VALUE_ERROR_HEADER_MARKERS):
        return ERR_HEADER_NOT_FOUND
    return ERR_UNKNOWN.format(details=str(error))


def humanize_save_error(error: Exception) -> str:
    """
    Отдельный текст для ошибок сохранения.

    Сохранение чаще всего падает из-за занятого файла
    или попытки записать в старый формат .xls.
    """
    if isinstance(error, InvalidFileException):
        return ERR_OLD_FORMAT

    if isinstance(error, BadZipFile):
        return ERR_FILE_CORRUPT

    if isinstance(error, (PermissionError, OSError)):
        return ERR_SAVE_FAILED
    return ERR_UNKNOWN.format(details=str(error))
