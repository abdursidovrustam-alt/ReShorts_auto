@echo off
chcp 65001 >nul
echo.
echo 📦 Установка React Frontend...
echo.

:: Проверка Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js не найден!
    echo    Установите Node.js 16+ с https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js версия:
node --version
echo.

:: Переход в папку client
if not exist "client" (
    echo ❌ Папка client не найдена!
    pause
    exit /b 1
)

cd client

:: Установка зависимостей
echo 📥 Установка npm пакетов...
echo    Это может занять несколько минут...
echo.
npm install

if %errorlevel% equ 0 (
    echo.
    echo ✅ Frontend зависимости установлены успешно!
    echo.
    echo 📋 Следующие шаги:
    echo    1. Запустите backend: run.bat
    echo    2. В новом окне: cd client ^&^& npm run dev
    echo    3. Откройте http://localhost:5173
) else (
    echo.
    echo ❌ Ошибка при установке зависимостей
)

echo.
cd ..
pause
