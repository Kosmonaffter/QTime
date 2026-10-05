"""
Точка входа приложения QTime.

Запускает окно Tkinter.
"""

from ui.app_window import AppWindow


def main():
    """Создаёт и запускает главное окно приложения."""
    AppWindow().mainloop()


if __name__ == "__main__":
    main()
