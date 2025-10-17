@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   ReShorts Windows - Установка системы
echo ==========================================
echo.

echo 🔍 Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo Установите Python 3.8+ с https://python.org
    pause
    exit /b 1
)

echo ✅ Python найден
python --version

echo.
echo 📦 Создание виртуального окружения...
if exist venv (
    echo Виртуальное окружение уже существует
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Ошибка создания виртуального окружения
        pause
        exit /b 1
    )
    echo ✅ Виртуальное окружение создано
)

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
echo 📥 Установка зависимостей...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей
    echo Проверьте подключение к интернету и попробуйте снова
    pause
    exit /b 1
)

echo ✅ Зависимости установлены

echo.
echo 📁 Создание необходимых папок...
if not exist logs mkdir logs
if not exist downloads mkdir downloads
if not exist processed mkdir processed
if not exist tmp mkdir tmp
if not exist output mkdir output

echo ✅ Папки созданы

echo.
echo 🎉 Установка завершена успешно!
echo.
echo Для запуска используйте:
echo   run.bat         - Запуск только backend
echo   run_dev.bat     - Запуск в режиме разработки
echo.
echo Приложение будет доступно по адресу:
echo   http://localhost:5000
echo.

pause