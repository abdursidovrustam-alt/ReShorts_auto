#!/bin/bash

# Скрипт установки зависимостей для ReShorts_auto
# Автор: MiniMax Agent
# Дата: 2025-10-17

echo "🚀 Начинаю установку ReShorts_auto..."
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8 или выше."
    exit 1
fi

echo "✅ Python версия: $(python3 --version)"
echo ""

# Создание виртуального окружения
echo "📦 Создание виртуального окружения..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
else
    echo "⚠️  Виртуальное окружение уже существует"
fi
echo ""

# Активация виртуального окружения
echo "🔄 Активация виртуального окружения..."
source venv/bin/activate

# Обновление pip
echo "⬆️  Обновление pip..."
pip install --upgrade pip
echo ""

# Установка зависимостей
echo "📥 Установка Python зависимостей..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Все зависимости установлены успешно"
else
    echo "❌ Ошибка при установке зависимостей"
    exit 1
fi
echo ""

# Установка Playwright браузеров
echo "🌐 Установка Playwright браузеров..."
playwright install
if [ $? -eq 0 ]; then
    echo "✅ Playwright браузеры установлены"
else
    echo "⚠️  Предупреждение: Не удалось установить Playwright браузеры"
fi
echo ""

# Создание необходимых папок
echo "📁 Создание необходимых директорий..."
mkdir -p logs
mkdir -p downloads
mkdir -p processed
echo "✅ Директории созданы: logs/, downloads/, processed/"
echo ""

# Проверка Node.js для React frontend
if command -v node &> /dev/null; then
    echo "✅ Node.js версия: $(node --version)"
    echo "✅ npm версия: $(npm --version)"
else
    echo "⚠️  Node.js не найден. Для React frontend потребуется Node.js 16+"
    echo "   Установите Node.js с https://nodejs.org/"
fi
echo ""

echo "🎉 Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "   1. Активируйте виртуальное окружение: source venv/bin/activate"
echo "   2. Запустите приложение: python app.py"
echo "   3. Откройте браузер: http://localhost:5000"
echo ""
echo "📖 Для подробной информации см. README.md"
