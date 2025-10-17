# Инструкция: Как получить YouTube Cookies для обхода bot detection

## Проблема
YouTube блокирует автоматическое скачивание видео, определяя запросы как действия бота. Решение - использовать cookies из браузера, чтобы имитировать авторизованный запрос от реального пользователя.

## Решение: Экспорт cookies из браузера

### Способ 1: Расширение "Get cookies.txt LOCALLY" (Рекомендуется)

#### Для Chrome/Edge:
1. Установите расширение ["Get cookies.txt LOCALLY"](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Откройте [youtube.com](https://www.youtube.com) и войдите в свой аккаунт
3. Кликните на иконку расширения
4. Нажмите "Export" для экспорта cookies в формате Netscape
5. Сохраните файл как `cookies.txt` в корне проекта `viral-shorts-master/`

#### Для Firefox:
1. Установите расширение ["cookies.txt"](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. Откройте [youtube.com](https://www.youtube.com) и войдите в свой аккаунт
3. Кликните на иконку расширения
4. Нажмите "Export cookies" 
5. Сохраните файл как `cookies.txt` в корне проекта `viral-shorts-master/`

### Способ 2: Использование yt-dlp для автоматического экспорта (если установлен браузер)

**ВАЖНО**: Этот способ не работает на серверах без установленного браузера!

```bash
# Для Chrome
yt-dlp --cookies-from-browser chrome --cookies cookies.txt "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Для Firefox
yt-dlp --cookies-from-browser firefox --cookies cookies.txt "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Где разместить файл cookies.txt

Файл `cookies.txt` должен находиться в корневой директории проекта:
```
viral-shorts-master/
├── cookies.txt          ← Здесь!
├── video_processor/
├── youtube_search/
└── ...
```

## Тестирование

После размещения `cookies.txt` запустите тест:

```bash
cd viral-shorts-master
python test_downloader.py
```

Если всё настроено правильно, вы увидите:
```
🍪 Использую cookies из файла: cookies.txt
📡 Подключение к YouTube через yt-dlp...
🔄 Начало загрузки видео...
✅ Видео успешно загружено!
```

## Важные замечания

1. **Безопасность**: Файл `cookies.txt` содержит данные вашей сессии YouTube. НЕ публикуйте его в открытом доступе!
2. **Срок действия**: Cookies имеют ограниченный срок действия. Если загрузка перестанет работать, обновите cookies.
3. **Ограничения**: Даже с cookies YouTube может блокировать слишком частые запросы. Используйте разумные интервалы между загрузками.
4. **Альтернатива**: Если у вас нет доступа к браузеру, рассмотрите использование сторонних API для загрузки видео.

## Устранение неполадок

### Ошибка: "Sign in to confirm you're not a bot"
- Убедитесь, что файл `cookies.txt` существует и находится в правильной директории
- Проверьте, что вы вошли в аккаунт YouTube перед экспортом cookies
- Попробуйте обновить cookies (они могли устареть)

### Ошибка: "HTTP Error 403: Forbidden"
- Cookies устарели или недействительны
- YouTube заблокировал ваш IP-адрес из-за частых запросов
- Попробуйте использовать VPN или прокси

### Предупреждение: "файл cookies не найден"
- Проверьте путь к файлу `cookies.txt`
- Убедитесь, что файл находится в корне проекта
- Проверьте права доступа к файлу

## Альтернативные решения (если cookies не помогают)

1. **Локальная разработка**: Разверните приложение локально, где у вас есть доступ к браузеру
2. **Сторонние API**: Используйте платные сервисы для загрузки YouTube видео
3. **Ручная загрузка**: Предложите пользователям загружать видео вручную через интерфейс
4. **Разрешение пользователя**: Попросите пользователей предоставить свои cookies.txt

## Ссылки

- [yt-dlp FAQ: Passing cookies](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)
- [Exporting YouTube cookies guide](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies)
