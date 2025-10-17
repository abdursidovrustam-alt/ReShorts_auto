# ReShorts Auto - Full-Stack Application

Современное full-stack приложение для автоматизации создания вирусных видео.

## Структура проекта

```
ReShorts_auto/
├── app.py                 # Улучшенный Flask backend
├── config.json            # Конфигурация системы
├── requirements.txt       # Python зависимости
├── modules/               # Модули загрузчиков
├── ai_analyzer/          # AI провайдеры
├── data/                 # Данные (статистика, пресеты)
└── client/               # React frontend приложение
    ├── src/
    │   ├── api/          # API клиент (axios)
    │   ├── components/   # UI компоненты
    │   ├── pages/        # Страницы приложения
    │   ├── layouts/      # Layout компоненты
    │   └── types/        # TypeScript типы
    ├── package.json
    └── vite.config.ts
```

## Технологический стек

### Backend
- **Flask 3.0** - веб-фреймворк
- **Flask-CORS** - поддержка CORS
- **yt-dlp** - загрузка с YouTube
- **instagrapi** - загрузка с Instagram
- **TikTokApi** - загрузка с TikTok

### Frontend
- **React 18** - UI библиотека
- **TypeScript** - типизация
- **Vite 6** - сборщик
- **Tailwind CSS** - стилизация
- **React Router v6** - роутинг
- **Axios** - HTTP клиент
- **Lucide React** - иконки

## Новые возможности

### Backend API

✅ **Поиск и предпросмотр**
- `POST /api/search/preview` - поиск видео с фильтрами
  - Параметры: platform, query, min_views, max_views, min_likes, duration_min/max, date_range, language, min_engagement, exclude_keywords
  - Возвращает: массив видео с полной информацией

- `GET /api/video/details/<video_id>` - детальная информация о видео

✅ **Фильтры и пресеты**
- `POST /api/filters/save` - сохранение пресета фильтров
- `GET /api/filters/list` - список сохранённых пресетов
- `DELETE /api/filters/delete/<preset_id>` - удаление пресета

✅ **Статистика**
- `GET /api/stats/dashboard` - полная статистика для дашборда
  - Количество скачанных, проанализированных, обработанных видео
  - График активности за 7 дней
  - Последние операции

### Frontend интерфейс

✅ **Страницы**
1. **Dashboard** - главная с статистикой
   - 4 статистические карточки
   - График активности за 7 дней
   - Последние операции

2. **Search & Preview** - поиск видео
   - Расширенные фильтры
   - Выбор платформы (YouTube, Instagram, TikTok)
   - Красивые карточки видео с превью

3. **Video Manager** - управление скачанными видео

4. **Settings** - настройки системы

5. **System Status** - статус загрузчиков и AI провайдеров

✅ **Дизайн**
- Modern Tech Dark тема
- Цвета: neutral-950/900/800 + cyan акценты (#06B6D4)
- Анимации 250-300ms
- Glow эффекты на интерактивных элементах
- Полностью responsive (desktop, tablet, mobile)

## Установка и запуск

### Backend

```bash
# Перейти в корневую папку
cd ReShorts_auto

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер (порт 5000)
python app.py
```

### Frontend

```bash
# Перейти в папку client
cd client

# Установить зависимости
pnpm install

# Запустить dev сервер (порт 5173)
pnpm run dev

# Или собрать для production
pnpm run build
```

### Доступ

- **Backend API**: http://localhost:5000
- **Frontend**: http://localhost:5173
- **Production**: https://1dms9jlo99ch.space.minimax.io

## API документация

### Поиск видео

```javascript
POST /api/search/preview

Request:
{
  "platform": "youtube",
  "query": "вирусные видео",
  "min_views": 10000,
  "max_views": 1000000,
  "min_engagement": 5.0
}

Response:
{
  "success": true,
  "total": 20,
  "videos": [
    {
      "id": "abc123",
      "title": "Как стать популярным",
      "views": 150000,
      "likes": 12000,
      "viral_score": 8.5,
      ...
    }
  ]
}
```

### Статистика

```javascript
GET /api/stats/dashboard

Response:
{
  "stats": {
    "total_downloaded": 0,
    "total_analyzed": 0,
    "total_processed": 0,
    "success_rate": 0
  },
  "activity_chart": [...],
  "recent_operations": [...]
}
```

## Структура данных

### Статистика
Хранится в `data/stats.json`:
```json
{
  "total_downloaded": 0,
  "total_analyzed": 0,
  "total_processed": 0,
  "success_rate": 0,
  "activity_log": [
    {
      "timestamp": "2025-10-17T15:32:25",
      "type": "download",
      "success": true
    }
  ]
}
```

### Пресеты фильтров
Хранятся в `data/filter_presets.json`:
```json
[
  {
    "id": "abc12345",
    "name": "Вирусные видео",
    "filters": {
      "min_views": 100000,
      "min_engagement": 5.0,
      "platform": "youtube"
    },
    "created_at": "2025-10-17T15:32:25"
  }
]
```

## Дизайн система

Полная спецификация: [docs/reshorts-auto-design-spec.md](docs/reshorts-auto-design-spec.md)

Дизайн-токены: [docs/design-tokens.json](docs/design-tokens.json)

### Основные цвета
- Primary: `#06B6D4` (cyan)
- Background: `#171717` (neutral-900)
- Surface: `#262626` (neutral-800)
- Text: `#F5F5F5` (neutral-100)

## Автор

MiniMax Agent

Дата: 2025-10-17

## Лицензия

MIT License
