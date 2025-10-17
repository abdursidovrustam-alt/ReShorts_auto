"""
Модуль для поиска вирусных видео на YouTube
Использует YouTube Data API v3
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class YouTubeSearcher:
    """Класс для поиска и анализа вирусных видео на YouTube"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация поисковика
        
        Args:
            api_key: API ключ YouTube Data API v3
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API ключ не найден! Укажите его в config.json или переменной окружения YOUTUBE_API_KEY")
        
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    def search_viral_videos(
        self,
        query: str,
        max_results: int = 20,
        days_ago: int = 30,
        min_views: int = 100000,
        video_duration: str = "short"  # short (< 4 мин), medium (4-20 мин), long (> 20 мин)
    ) -> List[Dict]:
        """
        Поиск вирусных видео по теме
        
        Args:
            query: Тема для поиска (например, "мотивация")
            max_results: Максимальное количество результатов
            days_ago: Искать видео за последние N дней
            min_views: Минимальное количество просмотров
            video_duration: Длительность видео (short/medium/long)
        
        Returns:
            Список словарей с информацией о видео
        """
        try:
            import requests
        except ImportError:
            raise ImportError("Установите библиотеку requests: pip install requests")
        
        # Рассчитываем дату для поиска
        published_after = (datetime.now() - timedelta(days=days_ago)).isoformat() + 'Z'
        
        # Параметры поиска
        search_params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'order': 'viewCount',  # Сортировка по просмотрам
            'maxResults': max_results,
            'publishedAfter': published_after,
            'videoDuration': video_duration,
            'key': self.api_key
        }
        
        # Выполняем поисковый запрос
        search_url = f"{self.base_url}/search"
        response = requests.get(search_url, params=search_params)
        
        if response.status_code != 200:
            error_data = response.json()
            raise Exception(f"Ошибка YouTube API: {error_data.get('error', {}).get('message', 'Неизвестная ошибка')}")
        
        search_data = response.json()
        
        if not search_data.get('items'):
            return []
        
        # Получаем ID видео
        video_ids = [item['id']['videoId'] for item in search_data['items']]
        
        # Получаем детальную статистику
        videos_info = self._get_videos_statistics(video_ids)
        
        # Фильтруем по минимальному количеству просмотров
        viral_videos = []
        for video in videos_info:
            if video['views'] >= min_views:
                viral_videos.append(video)
        
        # Сортируем по "вирусности" (engagement rate)
        viral_videos.sort(key=lambda x: x['engagement_rate'], reverse=True)
        
        return viral_videos
    
    def _get_videos_statistics(self, video_ids: List[str]) -> List[Dict]:
        """
        Получение детальной статистики для списка видео
        
        Args:
            video_ids: Список ID видео
        
        Returns:
            Список словарей со статистикой
        """
        try:
            import requests
        except ImportError:
            raise ImportError("Установите библиотеку requests: pip install requests")
        
        # Параметры запроса
        videos_params = {
            'part': 'snippet,statistics,contentDetails',
            'id': ','.join(video_ids),
            'key': self.api_key
        }
        
        videos_url = f"{self.base_url}/videos"
        response = requests.get(videos_url, params=videos_params)
        
        if response.status_code != 200:
            raise Exception(f"Ошибка при получении статистики: {response.status_code}")
        
        videos_data = response.json()
        
        result = []
        for item in videos_data.get('items', []):
            video_id = item['id']
            snippet = item['snippet']
            statistics = item['statistics']
            content_details = item['contentDetails']
            
            # Парсим статистику
            views = int(statistics.get('viewCount', 0))
            likes = int(statistics.get('likeCount', 0))
            comments = int(statistics.get('commentCount', 0))
            
            # Вычисляем engagement rate (вовлеченность)
            engagement_rate = 0
            if views > 0:
                engagement_rate = ((likes + comments) / views) * 100
            
            # Парсим длительность видео (формат ISO 8601: PT1M30S)
            duration = self._parse_duration(content_details.get('duration', ''))
            
            video_info = {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail': snippet['thumbnails'].get('high', {}).get('url', ''),
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'views': views,
                'likes': likes,
                'comments': comments,
                'engagement_rate': round(engagement_rate, 2),
                'duration_seconds': duration,
                'tags': snippet.get('tags', [])
            }
            
            result.append(video_info)
        
        return result
    
    def _parse_duration(self, duration_str: str) -> int:
        """
        Преобразование длительности из формата ISO 8601 в секунды
        
        Args:
            duration_str: Строка формата PT1M30S
        
        Returns:
            Длительность в секундах
        """
        import re
        
        # Парсим формат PT1H2M30S
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def get_trending_topics(self, category: str = "entertainment") -> List[Dict]:
        """
        Получение трендовых тем в определенной категории
        
        Args:
            category: Категория (entertainment, music, sports, gaming, etc.)
        
        Returns:
            Список трендовых видео
        """
        # Mapping категорий к YouTube category IDs
        category_map = {
            "entertainment": "24",
            "music": "10",
            "sports": "17",
            "gaming": "20",
            "education": "27",
            "howto": "26",
            "comedy": "23"
        }
        
        category_id = category_map.get(category.lower(), "0")
        
        try:
            import requests
        except ImportError:
            raise ImportError("Установите библиотеку requests: pip install requests")
        
        # Параметры запроса
        params = {
            'part': 'snippet,statistics',
            'chart': 'mostPopular',
            'regionCode': 'RU',  # Можно изменить на другую страну
            'videoCategoryId': category_id,
            'maxResults': 20,
            'key': self.api_key
        }
        
        videos_url = f"{self.base_url}/videos"
        response = requests.get(videos_url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Ошибка при получении трендов: {response.status_code}")
        
        videos_data = response.json()
        
        result = []
        for item in videos_data.get('items', []):
            video_id = item['id']
            snippet = item['snippet']
            statistics = item['statistics']
            
            result.append({
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'thumbnail': snippet['thumbnails'].get('high', {}).get('url', ''),
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'views': int(statistics.get('viewCount', 0)),
                'likes': int(statistics.get('likeCount', 0))
            })
        
        return result


# Вспомогательная функция для быстрого использования
def search_youtube_videos(query: str, api_key: str, max_results: int = 20) -> List[Dict]:
    """
    Быстрая функция для поиска YouTube видео
    
    Args:
        query: Тема для поиска
        api_key: YouTube API ключ
        max_results: Максимальное количество результатов
    
    Returns:
        Список видео с информацией
    """
    searcher = YouTubeSearcher(api_key=api_key)
    return searcher.search_viral_videos(query=query, max_results=max_results)
