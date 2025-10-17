@echo off
chcp 65001 >nul
echo.
echo 🚀 Запуск в режиме разработки...
echo.

:: Проверка виртуального окружения
if not exist "venv" (
    echo ❌ Backend не установлен! Запустите setup.bat
    pause
    exit /b 1
)

:: Проверка frontend
if not exist "client\node_modules" (
    echo ❌ Frontend не установлен! Запустите install_frontend.bat
    pause
    exit /b 1
)

echo ✅ Запуск backend и frontend серверов...
echo.
echo 📝 Backend: http://localhost:5000
echo 📝 Frontend: http://localhost:5173
echo.
echo 💡 Нажмите Ctrl+C для остановки серверов
echo.

:: Запуск backend в фоновом режиме
start "ReShorts Backend" cmd /c "call venv\Scripts\activate.bat && python app.py"

:: Небольшая пауза
timeout /t 3 /nobreak >nul

:: Запуск frontend
cd client
start "ReShorts Frontend" cmd /c "npm run dev"

echo.
echo ✅ Оба сервера запущены в отдельных окнах!
echo    Закройте окна для остановки серверов.
echo.
pause
