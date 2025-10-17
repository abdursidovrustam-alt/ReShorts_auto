# 📥 Модуль загрузки видео (Video Downloader)

## Текущий статус: ✅ ГОТОВ (требуется настройка)

### Реализованный функционал

Модуль `video_processor/downloader.py` полностью реализован и использует:
- **yt-dlp** (версия 2025.10.14) - самый актуальный инструмент для загрузки с YouTube
- **Cookies-based аутентификация** - единственный надежный способ обхода YouTube bot detection
- **iOS/Web player клиенты** - дополнительная защита от блокировки

## 🔧 Обязательная настройка

### Шаг 1: Получите файл cookies.txt

**БЕЗ ЭТОГО ШАГА ЗАГРУЗКА НЕ БУДЕТ РАБОТАТЬ!**

Подробная инструкция: **[COOKIES_SETUP.md](./COOKIES_SETUP.md)**

Краткая версия:
1. Установите расширение "Get cookies.txt LOCALLY" в Chrome/Firefox
2. Откройте youtube.com и войдите в аккаунт
3. Экспортируйте cookies в файл `cookies.txt`
4. Поместите файл в корень проекта: `viral-shorts-master/cookies.txt`

### Шаг 2: Тестирование

```bash
cd viral-shorts-master
python test_downloader.py
```

**Ожидаемый результат:**
```
🍪 Использую cookies из файла: cookies.txt
📡 Подключение к YouTube через yt-dlp...
🔄 Начало загрузки видео...
✅ Видео успешно загружено!
📺 Название: [название видео]
💾 Файл: downloads/[название].mp4
```

## 📖 API документация

### Класс VideoDownloader

```python
from video_processor.downloader import VideoDownloader

# Инициализация
downloader = VideoDownloader(cookies_file='cookies.txt')

# Загрузка одного видео
result = downloader.download_video(
    video_url='https://www.youtube.com/shorts/XXXXXXXXX',
    output_path='downloads/',
    quality='highest'  # 'highest', '720p', '480p', '360p', '144p'
)

# Проверка результата
if result['success']:
    print(f"Файл: {result['file_path']}")
    print(f"Название: {result['title']}")
    print(f"Длительность: {result['duration']} сек")
else:
    print(f"Ошибка: {result['error']}")
```

### Функция download_video (упрощенный вариант)

```python
from video_processor.downloader import download_video

result = download_video(
    'https://www.youtube.com/shorts/XXXXXXXXX',
    output_path='downloads/',
    quality='highest',
    cookies_file='cookies.txt'
)
```

### Загрузка нескольких видео

```python
urls = [
    'https://www.youtube.com/shorts/VIDEO1',
    'https://www.youtube.com/shorts/VIDEO2',
    'https://www.youtube.com/shorts/VIDEO3',
]

downloader = VideoDownloader()
results = downloader.download_multiple_videos(urls, output_path='downloads/')

for i, result in enumerate(results):
    if result['success']:
        print(f"✅ Видео {i+1}: {result['title']}")
    else:
        print(f"❌ Видео {i+1}: {result['error']}")
```

## 🔍 Структура результата

```python
{
    'success': True,          # bool - успешность операции
    'file_path': str,         # путь к загруженному файлу
    'title': str,             # название видео
    'duration': int,          # длительность в секундах
    'video_id': str,          # ID видео на YouTube
    'view_count': int,        # количество просмотров
    'resolution': str,        # разрешение (например "1920x1080")
    'filesize_mb': float,     # размер файла в MB
    'error': str              # текст ошибки (если success=False)
}
```

## ⚠️ Важные ограничения

### 1. Cookies обязательны
- Без файла `cookies.txt` загрузка будет заблокирована YouTube
- Cookies нужно периодически обновлять (каждые 1-3 месяца)

### 2. Безопасность
- НЕ публикуйте файл `cookies.txt` в Git
- Файл добавлен в `.gitignore`
- Cookies содержат вашу сессию YouTube - храните их в секрете!

### 3. Частота запросов
- Не делайте слишком много запросов подряд
- YouTube может заблокировать IP при подозрительной активности
- Рекомендуемый интервал: минимум 5-10 секунд между загрузками

### 4. Легальность
- Скачивание видео может нарушать Terms of Service YouTube
- Используйте только для личных, некоммерческих целей
- Не перезагружайте чужой контент без разрешения автора

## 🐛 Устранение неполадок

### Ошибка: "файл cookies не найден"
✅ **Решение:** Убедитесь, что файл `cookies.txt` находится в корне проекта

### Ошибка: "Sign in to confirm you're not a bot"
✅ **Решение:** 
- Проверьте, что cookies актуальны (войдите в YouTube и обновите cookies)
- Убедитесь, что вы вошли в аккаунт YouTube перед экспортом cookies

### Ошибка: "HTTP Error 403: Forbidden"
✅ **Решение:**
- Cookies устарели - обновите их
- Слишком много запросов - подождите несколько минут
- Попробуйте использовать VPN

### Permission error accessing plugins
⚠️ **Известная проблема:** Это предупреждение можно игнорировать. Оно не влияет на работу загрузчика.

## 📚 Дополнительные ресурсы

- [COOKIES_SETUP.md](./COOKIES_SETUP.md) - Подробная инструкция по настройке cookies
- [YOUTUBE_LIMITATION.md](./YOUTUBE_LIMITATION.md) - Информация об ограничениях YouTube
- [yt-dlp документация](https://github.com/yt-dlp/yt-dlp)
- [yt-dlp FAQ](https://github.com/yt-dlp/yt-dlp/wiki/FAQ)

## 🎯 Следующие шаги

1. ✅ **Модуль загрузки** - Готов (требуется cookies.txt)
2. ⏳ **Модуль обработки видео** - В разработке
3. ⏳ **Веб-интерфейс** - Планируется
4. ⏳ **Flask бэкенд** - Планируется
