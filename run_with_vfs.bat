@echo off
chcp 65001 >nul
echo Запуск эмулятора с VFS...
python -m src.main --vfs vfs.json
pause
