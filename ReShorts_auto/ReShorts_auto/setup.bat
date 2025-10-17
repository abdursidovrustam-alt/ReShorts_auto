@echo off
chcp 65001 >nul
echo.
echo 🚀 Начинаю установку ReShorts_auto...
echo.

:: Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден. Установите Python 3.8 или выше.
    echo    Скачайте с https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python версия:
python --version
echo.

:: Создание виртуального окружения
echo 📦 Создание виртуального окружения...
if not exist "venv" (
    python -m venv venv
    echo ✅ Виртуальное окружение создано
) else (
    echo ⚠️  Виртуальное окружение уже существует
)
echo.

:: Активация виртуального окружения
echo 🔄 Активация виртуального окружения...
call venv\Scripts\activate.bat

:: Обновление pip
echo ⬆️  Обновление pip...
python -m pip install --upgrade pip
echo.

:: Установка зависимостей
echo 📥 Установка Python зависимостей...
pip install -r requirements.txt
if %errorlevel% equ 0 (
    echo ✅ Все зависимости установлены успешно
) else (
    echo ❌ Ошибка при установке зависимостей
    pause
    exit /b 1
)
echo.

:: Установка Playwright браузеров
echo 🌐 Установка Playwright браузеров...
playwright install
if %errorlevel% equ 0 (
    echo ✅ Playwright браузеры установлены
) else (
    echo ⚠️  Предупреждение: Не удалось установить Playwright браузеры
)
echo.

:: Создание необходимых папок
echo 📁 Создание необходимых директорий...
if not exist "logs" mkdir logs
if not exist "downloads" mkdir downloads
if not exist "processed" mkdir processed
if not exist "tmp" mkdir tmp
if not exist "output" mkdir output
echo ✅ Директории созданы: logs/, downloads/, processed/, tmp/, output/
echo.

:: Проверка Node.js для React frontend
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Node.js версия:
    node --version
    echo ✅ npm версия:
    npm --version
) else (
    echo ⚠️  Node.js не найден. Для React frontend потребуется Node.js 16+
    echo    Установите Node.js с https://nodejs.org/
)
echo.

echo 🎉 Установка завершена!
echo.
echo 📋 Следующие шаги:
echo    1. Активируйте виртуальное окружение: venv\Scripts\activate
echo    2. Запустите приложение: python app.py
echo    3. Откройте браузер: http://localhost:5000
echo.
echo 📖 Для подробной информации см. README.md
echo.
pause
