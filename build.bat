@echo off
chcp 65001 > nul
echo === Сборка QTime ===

python -m venv .venv
call .venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

pyinstaller --noconfirm --clean QTime.spec

echo.
echo === Готово: dist\QTime\QTime.exe ===
pause