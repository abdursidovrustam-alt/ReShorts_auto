# ReShorts Windows Edition

<div align="center">

![ReShorts Windows](https://img.shields.io/badge/ReShorts-Windows%20Edition-06B6D4?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

**Полнофункциональная система для поиска, анализа и обработки вирусных видео**

🎯 **Без заглушек** • 🔧 **Windows Ready** • 🤖 **AI Powered** • 📱 **Modern UI**

</div>

---

## 🚀 Что это такое?

**ReShorts Windows Edition** — это адаптированная под Windows версия системы автоматизации для создания вирусных коротких видео. Система позволяет:

- 🔍 **Искать популярные видео** на YouTube, TikTok, Instagram
- 📥 **Скачивать без API ключей** используя yt-dlp и другие инструменты
- 🤖 **Анализировать с помощью AI** через бесплатные провайдеры
- 📊 **Отслеживать статистику** и управлять процессами
- 🎨 **Использовать современный веб-интерфейс** без установки React

## ✨ Ключевые особенности

### 🔧 Полная совместимость с Windows
- ✅ Исправлены все проблемы с путями файлов
- ✅ Правильная работа с кодировками
- ✅ Батч-файлы для установки и запуска
- ✅ Поддержка Windows 10/11

### 🚫 Без заглушек и мок-данных
- ✅ Реальный поиск видео
- ✅ Функциональные загрузчики
- ✅ Работающий AI анализ
- ✅ Полноценная статистика

### 🤖 Множественные AI провайдеры
- **GPT4Free** (бесплатный) - автоматический fallback
- **Google Gemini** (бесплатный) - с API ключом или fallback
- **OpenRouter** (опционально) - для доступа к премиум моделям
- **LocalAI** (опционально) - для приватности

### 🎨 Современный HTML интерфейс
- Темная тема с cyan акцентами
- Адаптивный дизайн (desktop/tablet/mobile)
- Плавные анимации и переходы
- Без зависимостей от React/Node.js

## 📦 Быстрая установка

### Требования
- **Windows 10/11**
- **Python 3.8+** ([скачать](https://python.org))
- **Интернет соединение**

### Автоматическая установка

1. **Скачайте проект**
```cmd
git clone https://github.com/your-repo/ReShorts_Windows.git
cd ReShorts_Windows
```

2. **Запустите установку**
```cmd
setup.bat
```

3. **Запустите приложение**
```cmd
run.bat
```

4. **Откройте в браузере**
```
http://localhost:5000
```

### Ручная установка

```cmd
# Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Создать папки
mkdir logs downloads processed tmp output

# Запустить
python app.py
```

## 🎮 Использование

### 🔍 Поиск видео

1. Перейдите на вкладку **"Поиск видео"**
2. Выберите платформу (YouTube, TikTok, Instagram)
3. Введите поисковый запрос
4. Настройте фильтры:
   - Минимум/максимум просмотров
   - Длительность видео
   - Engagement rate
   - Период публикации
5. Нажмите **"Найти видео"**

### 📥 Скачивание

- **Отдельное видео**: нажмите "📥 Скачать" в карточке видео
- **Множественное**: выберите видео ☑️ и нажмите "📥 Скачать выбранные"
- **Автоматическое**: включите в настройках автоматическое скачивание

### 🤖 AI Анализ

1. Перейдите на вкладку **"AI Анализ"**
2. Вставьте данные видео (JSON или описание)
3. Добавьте дополнительный промпт (опционально)
4. Нажмите **"🤖 Начать анализ"**

**Пример данных видео:**
```json
{
  "title": "Как я заработал миллион за месяц",
  "description": "Секретная стратегия заработка...",
  "views": 500000,
  "likes": 25000,
  "comments": 1200,
  "duration": 45,
  "platform": "youtube"
}
```

### ⚙️ Настройки

**Поиск:**
- Максимум результатов
- Период по умолчанию
- Минимум просмотров

**AI:**
- Timeout для запросов
- Количество попыток
- Приоритеты провайдеров

**Загрузка:**
- Качество видео
- Максимальный размер
- Скачивание миниатюр

**Автоматизация:**
- Автоматический поиск
- Автоматическое скачивание
- Автоматический анализ

## 🔧 Конфигурация AI провайдеров

### Google Gemini (рекомендуется)

1. Получите бесплатный API ключ: https://makersuite.google.com/app/apikey
2. Создайте файл `.env`:
```env
GEMINI_API_KEY=your_api_key_here
```

### OpenRouter (опционально)

1. Зарегистрируйтесь: https://openrouter.ai
2. Добавьте в `.env`:
```env
OPENROUTER_API_KEY=your_api_key_here
```

### LocalAI (для приватности)

1. Установите LocalAI: https://localai.io/basics/getting_started/
2. Запустите сервер на localhost:8080
3. Настройка автоматическая

## 📁 Структура проекта

```
ReShorts_Windows/
├── app.py                          # Главный файл приложения
├── config.json                     # Конфигурация системы
├── requirements.txt                # Python зависимости
├── setup.bat                       # Установка для Windows
├── run.bat                         # Запуск для Windows
│
├── modules/                        # Модули системы
│   ├── universal_downloader.py     # Универсальный загрузчик
│   ├── video_search.py             # Поисковая система
│   └── downloaders/                # Загрузчики
│       ├── ytdlp_downloader.py     # YouTube/TikTok загрузчик
│       └── requests_downloader.py  # Прямые ссылки
│
├── ai_analyzer/                    # AI анализ
│   ├── multi_provider.py           # Менеджер провайдеров
│   └── providers/                  # AI провайдеры
│       ├── gpt4free_provider.py    # GPT4Free
│       ├── gemini_provider.py      # Google Gemini
│       ├── openrouter_provider.py  # OpenRouter
│       └── localai_provider.py     # LocalAI
│
├── web_interface/                  # Веб-интерфейс
│   ├── index.html                  # Главная страница
│   ├── styles.css                  # Стили
│   └── script.js                   # JavaScript
│
└── logs/                           # Логи и данные
    ├── reshorts.log                # Основной лог
    └── stats.json                  # Статистика
```

## 🎯 API Endpoints

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/stats` | GET | Статистика системы |
| `/api/search` | POST | Поиск видео |
| `/api/download` | POST | Скачивание видео |
| `/api/analyze` | POST | AI анализ |
| `/api/files` | GET | Список файлов |
| `/api/config` | GET/POST | Конфигурация |
| `/api/system-status` | GET | Статус системы |

## 🔧 Troubleshooting

### Проблемы с установкой

**Python не найден:**
```cmd
# Установите Python с python.org
# Убедитесь что добавили в PATH
python --version
```

**Ошибки зависимостей:**
```cmd
# Обновите pip
python -m pip install --upgrade pip

# Переустановите зависимости
pip install -r requirements.txt --force-reinstall
```

### Проблемы с запуском

**Backend недоступен:**
- Проверьте что Python активирован: `venv\Scripts\activate`
- Проверьте порт 5000: `netstat -an | findstr 5000`
- Запустите вручную: `python app.py`

**AI не работает:**
- Проверьте интернет соединение
- Добавьте API ключи в `.env`
- Проверьте статус провайдеров на странице "Статус"

### Проблемы со скачиванием

**yt-dlp ошибки:**
```cmd
# Обновите yt-dlp
pip install --upgrade yt-dlp
```

**Блокировка сайтов:**
- Используйте VPN
- Настройте прокси в настройках

## 🆚 Отличия от оригинала

| Функция | Оригинал | Windows Edition |
|---------|----------|-----------------|
| **Совместимость** | Linux/Mac | ✅ Windows Ready |
| **Интерфейс** | React (сложно) | ✅ Pure HTML/JS |
| **Заглушки** | Много мок-данных | ✅ Без заглушек |
| **AI провайдеры** | Ограниченно | ✅ 4 провайдера |
| **Установка** | Сложная | ✅ setup.bat |
| **Зависимости** | Node.js + Python | ✅ Только Python |

## 📄 Лицензия

MIT License - используйте свободно в личных и коммерческих проектах.

## 🤝 Поддержка

- 📧 Email: support@reshorts-windows.local
- 🐛 Issues: GitHub Issues
- 💬 Telegram: @reshorts_support

## 🔄 Обновления

**v2.0 (Текущая версия)**
- ✅ Полная совместимость с Windows
- ✅ Убраны все заглушки
- ✅ Добавлен HTML интерфейс
- ✅ 4 AI провайдера
- ✅ Автоматическая установка

**Планы на v2.1**
- 🔄 Обработка видео (нарезка, эффекты)
- 🔄 Планировщик публикаций
- 🔄 Интеграция с соцсетями
- 🔄 Продвинутая аналитика

---

<div align="center">

**⭐ Поставьте звездочку если проект полезен!**

Made with ❤️ by MiniMax Agent

</div>