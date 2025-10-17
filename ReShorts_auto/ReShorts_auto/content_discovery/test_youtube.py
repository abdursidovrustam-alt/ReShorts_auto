"""
Тестовый пример использования модуля поиска YouTube
"""

import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from content_discovery.youtube_search import YouTubeSearcher


def test_youtube_search():
    """Тестовая функция для демонстрации работы поиска"""
    
    print("=" * 60)
    print("🔍 ТЕСТ МОДУЛЯ ПОИСКА YOUTUBE ВИДЕО")
    print("=" * 60)
    
    # ВАЖНО: Замените на свой API ключ!
    # Как получить: https://console.cloud.google.com/apis/credentials
    api_key = "YOUR_YOUTUBE_API_KEY_HERE"
    
    if api_key == "YOUR_YOUTUBE_API_KEY_HERE":
        print("\n⚠️ ВНИМАНИЕ: Необходимо указать YouTube API ключ!")
        print("\n📝 Инструкция по получению API ключа:")
        print("1. Перейдите на: https://console.cloud.google.com/")
        print("2. Создайте новый проект или выберите существующий")
        print("3. Перейдите в 'APIs & Services' → 'Credentials'")
        print("4. Нажмите 'Create Credentials' → 'API key'")
        print("5. Включите 'YouTube Data API v3' в библиотеке API")
        print("6. Скопируйте ключ и замените в config.json или здесь")
        print("\n💰 Бесплатный лимит: 10,000 запросов в день (достаточно!)")
        return
    
    try:
        # Создаем экземпляр поисковика
        searcher = YouTubeSearcher(api_key=api_key)
        
        # Тест 1: Поиск вирусных видео по теме
        print("\n🎯 Тест 1: Поиск вирусных видео на тему 'мотивация'")
        print("-" * 60)
        
        videos = searcher.search_viral_videos(
            query="мотивация успех",
            max_results=5,
            days_ago=30,
            min_views=50000,
            video_duration="short"  # Короткие видео (< 4 минут)
        )
        
        print(f"\n✅ Найдено {len(videos)} вирусных видео:\n")
        
        for i, video in enumerate(videos, 1):
            print(f"{i}. {video['title'][:50]}...")
            print(f"   📺 Канал: {video['channel_title']}")
            print(f"   👁️  Просмотров: {video['views']:,}")
            print(f"   👍 Лайков: {video['likes']:,}")
            print(f"   💬 Комментариев: {video['comments']:,}")
            print(f"   📊 Вовлеченность: {video['engagement_rate']:.2f}%")
            print(f"   ⏱️  Длительность: {video['duration_seconds']} сек")
            print(f"   🔗 URL: {video['url']}")
            print()
        
        # Тест 2: Получение трендовых видео
        print("\n🔥 Тест 2: Топ трендовых видео в категории 'развлечения'")
        print("-" * 60)
        
        trending = searcher.get_trending_topics(category="entertainment")
        
        print(f"\n✅ Найдено {len(trending)} трендовых видео:\n")
        
        for i, video in enumerate(trending[:5], 1):
            print(f"{i}. {video['title'][:50]}...")
            print(f"   📺 Канал: {video['channel_title']}")
            print(f"   👁️  Просмотров: {video['views']:,}")
            print(f"   🔗 URL: {video['url']}")
            print()
        
        print("=" * 60)
        print("✅ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {str(e)}")
        print("\nВозможные причины:")
        print("1. Неверный API ключ")
        print("2. API ключ не активирован для YouTube Data API v3")
        print("3. Превышен лимит запросов (10,000 в день)")
        print("4. Не установлена библиотека 'requests': pip install requests")


if __name__ == "__main__":
    test_youtube_search()
