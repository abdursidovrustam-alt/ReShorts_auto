@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo     ReShorts Windows - Запуск системы
echo ==========================================
echo.

echo 🔍 Проверка виртуального окружения...
if not exist venv (
    echo ❌ Виртуальное окружение не найдено!
    echo Запустите setup.bat для установки
    pause
    exit /b 1
)

echo ✅ Виртуальное окружение найдено

echo.
echo 🔧 Активация виртуального окружения...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Ошибка активации виртуального окружения
    pause
    exit /b 1
)

echo ✅ Виртуальное окружение активировано

echo.
echo 🚀 Запуск ReShorts...
echo.
echo Приложение будет доступно по адресу:
echo   http://localhost:5000
echo.
echo Для остановки нажмите Ctrl+C
echo.

python app.py

echo.
echo ⛔ ReShorts остановлен
pause