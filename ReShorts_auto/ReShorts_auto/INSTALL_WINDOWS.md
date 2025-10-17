# Инструкция по установке ReShorts Auto на Windows

## 📋 Требования

Перед установкой убедитесь, что у вас установлены:

### 1. Python 3.8 или выше
**Скачать:** https://www.python.org/downloads/

✅ При установке **обязательно** отметьте:
- ☑️ "Add Python to PATH"
- ☑️ "Install pip"

**Проверка установки:**
```cmd
python --version
```
Должно показать: `Python 3.8.x` или выше

### 2. Node.js 16 или выше
**Скачать:** https://nodejs.org/

Рекомендуется **LTS версия** (Long Term Support)

**Проверка установки:**
```cmd
node --version
npm --version
```

### 3. Git (опционально, для клонирования)
**Скачать:** https://git-scm.com/download/win

---

## 🚀 Установка проекта

### Вариант 1: Клонирование через Git (рекомендуется)

```cmd
# Открыть командную строку (Win+R -> cmd)
# Перейти в папку, где хотите разместить проект
cd C:\Projects

# Клонировать репозиторий
git clone https://github.com/abdursidovrustam-alt/ReShorts_auto.git

# Перейти в папку проекта
cd ReShorts_auto
```

### Вариант 2: Скачать ZIP архив

1. Откройте: https://github.com/abdursidovrustam-alt/ReShorts_auto
2. Нажмите зелёную кнопку **"Code"** → **"Download ZIP"**
3. Распакуйте архив в любую папку
4. Откройте командную строку в этой папке:
   - Shift + Правая кнопка мыши → "Открыть окно команд здесь"
   - Или: Win+R → cmd → cd путь_к_папке

---

## ⚙️ Настройка проекта

### Шаг 1: Установка Backend

```cmd
setup.bat
```

Этот скрипт автоматически:
- ✅ Создаст виртуальное окружение Python
- ✅ Установит все Python зависимости (Flask, yt-dlp, и др.)
- ✅ Установит Playwright браузеры
- ✅ Создаст необходимые папки

⏱️ Установка займёт 2-5 минут

### Шаг 2: Установка Frontend

**В новом окне командной строки:**

```cmd
install_frontend.bat
```

Этот скрипт:
- ✅ Установит все Node.js зависимости (React, Vite, и др.)

⏱️ Установка займёт 3-7 минут (зависит от интернета)

---

## 🎮 Запуск приложения

### Вариант A: Автоматический запуск (рекомендуется)

```cmd
run_dev.bat
```

✨ Откроется **2 окна**:
- 🟢 **Backend** на http://localhost:5000
- 🔵 **Frontend** на http://localhost:5173

**Откройте браузер:** http://localhost:5173

### Вариант B: Запустить только Backend

```cmd
run.bat
```

---

## 📂 Структура проекта

```
ReShorts_auto/
├── 📄 setup.bat                    # Установка Backend
├── 📄 install_frontend.bat         # Установка Frontend
├── 📄 run.bat                      # Запуск Backend
├── 📄 run_dev.bat                  # Запуск Backend + Frontend
├── 📄 app.py                       # Главный сервер Flask
├── 📄 config.json                  # Настройки системы
├── 📄 requirements.txt             # Python зависимости
│
├── 📁 venv/                        # Виртуальное окружение Python (создаётся автоматически)
│
├── 📁 modules/                     # Модули загрузчиков
│   ├── universal_downloader.py
│   └── downloaders/
│       ├── ytdlp_downloader.py     # YouTube загрузчик
│       ├── instagrapi_downloader.py # Instagram
│       └── tiktok_downloader.py    # TikTok
│
├── 📁 ai_analyzer/                 # AI модули
│   ├── multi_provider.py
│   └── providers/
│       ├── gpt4free_provider.py
│       ├── gemini_provider.py
│       └── ...
│
├── 📁 client/                      # React приложение
│   ├── 📄 package.json
│   ├── 📄 vite.config.ts
│   ├── 📄 tailwind.config.js
│   ├── 📁 node_modules/            # (создаётся автоматически)
│   └── 📁 src/
│       ├── 📁 api/                 # API клиент
│       ├── 📁 components/          # UI компоненты
│       ├── 📁 pages/               # Страницы
│       ├── 📁 layouts/
│       └── 📁 types/
│
├── 📁 logs/                        # Логи (создаётся автоматически)
├── 📁 downloads/                   # Скачанные видео
├── 📁 processed/                   # Обработанные видео
├── 📁 tmp/                         # Временные файлы
└── 📁 docs/                        # Документация
```

---

## 🔧 Решение проблем

### ❌ "Python не найден"

**Решение:**
1. Переустановите Python с https://www.python.org/downloads/
2. При установке отметьте "Add Python to PATH"
3. Перезапустите командную строку

### ❌ "Node.js не найден"

**Решение:**
1. Установите Node.js с https://nodejs.org/
2. Перезапустите командную строку

### ❌ "'pip' не является внутренней или внешней командой"

**Решение:**
```cmd
python -m ensurepip --upgrade
```

### ❌ "Ошибка при установке зависимостей"

**Решение:**
```cmd
# Обновить pip
python -m pip install --upgrade pip

# Повторить установку
pip install -r requirements.txt
```

### ❌ "playwright install не работает"

**Решение:**
```cmd
# Активировать виртуальное окружение
venv\Scripts\activate

# Установить Playwright вручную
pip install playwright
playwright install
```

### ❌ Frontend не запускается

**Решение:**
```cmd
cd client

# Очистить кэш
rmdir /s /q node_modules
del package-lock.json

# Переустановить
npm install
```

---

## 📞 Дополнительная помощь

### Где находятся логи?
```
logs/reshorts.log
```

### Как изменить настройки?
1. Откройте `config.json` в текстовом редакторе
2. Или используйте UI: http://localhost:5173 → Settings

### Как остановить серверы?
- Нажмите **Ctrl+C** в окнах командной строки
- Или закройте окна

---

## ✅ Что дальше?

1. **Откройте приложение:** http://localhost:5173
2. **Изучите документацию:** [README.md](README.md)
3. **Начните работу:** перейдите в раздел "Search & Preview"

---

**Дата создания:** 2025-10-17  
**Автор:** MiniMax Agent
