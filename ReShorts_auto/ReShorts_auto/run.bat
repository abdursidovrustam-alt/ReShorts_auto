@echo off
chcp 65001 >nul
echo.
echo 🚀 Запуск ReShorts Auto...
echo.

:: Проверка виртуального окружения
if not exist "venv" (
    echo ❌ Виртуальное окружение не найдено!
    echo    Запустите setup.bat для установки
    pause
    exit /b 1
)

:: Активация виртуального окружения
echo 🔄 Активация виртуального окружения...
call venv\Scripts\activate.bat

:: Запуск приложения
echo ✅ Запуск Flask сервера...
echo 📝 Backend запущен на http://localhost:5000
echo.
echo ⏳ Ожидание запуска сервера (3 секунды)...
echo.

:: Запуск сервера в фоне и открытие браузера
start /B python app.py

:: Ожидание 3 секунды для запуска сервера
timeout /t 3 /nobreak >nul

:: Открытие браузера
echo 🌐 Открытие браузера...
start http://localhost:5000

echo.
echo ✅ Интерфейс открыт в браузере!
echo.
echo 💡 Для остановки сервера закройте это окно
echo.

:: Ожидание завершения процесса Python
wait
