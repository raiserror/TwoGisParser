@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════╗
echo ║                   Парсер 2GIS                    ║
echo ╚══════════════════════════════════════════════════╝
echo.

echo.
echo Устанавливаем зависимости...
pip install sv-ttk
pip install pyinstaller
pip install googletrans
pip uninstall playwright -y
pip install playwright
pip install openpyxl
pip install asyncio
playwright install chromium

echo.
echo Собираем EXE...
pyinstaller --clean --noconfirm ^
--name="2GIS_Parser" ^
--onefile ^
--windowed ^
--icon="static/icon.ico" ^
--add-data="static;static" ^
--add-data="%LOCALAPPDATA%\ms-playwright;ms-playwright" ^
--runtime-hook=playwright_runtime_hook.py ^
gui_main.py

echo.
pause