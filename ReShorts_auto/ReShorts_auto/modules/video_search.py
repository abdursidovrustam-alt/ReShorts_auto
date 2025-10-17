"""
Модуль для реального поиска видео на различных платформах
Использует yt-dlp для поиска на YouTube и других платформах
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import subprocess
import json

logger = logging.getLogger(__name__)


class VideoSearchEngine:
    """Поисковик видео на различных платформах"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def search_youtube(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Поиск видео на YouTube с использованием yt-dlp"""
        try:
            logger.info(f"Поиск на YouTube: {query}")
            
            # Формируем поисковый запрос для yt-dlp
            search_query = f"ytsearch{max_results}:{query}"
            
            # Выполняем поиск через yt-dlp
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-warnings',
                '--skip-download',
                '--flat-playlist',
                search_query
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Ошибка yt-dlp: {result.stderr}")
                return []
            
            # Парсим результаты
            videos = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    video_data = json.loads(line)
                    video = self._parse_youtube_video(video_data)
                    if video:
                        videos.append(video)
                except json.JSONDecodeError:
                    continue
            
            logger.info(f"Найдено {len(videos)} видео")
            return videos
            
        except subprocess.TimeoutExpired:
            logger.error("Превышено время ожидания поиска")
            return []
        except Exception as e:
            logger.error(f"Ошибка поиска на YouTube: {e}")
            return []
    
    def _parse_youtube_video(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Парсинг данных видео из yt-dlp"""
        try:
            video_id = data.get('id', '')
            if not video_id:
                return None
            
            # Получаем статистику
            view_count = data.get('view_count', 0) or 0
            like_count = data.get('like_count', 0) or 0
            comment_count = data.get('comment_count', 0) or 0
            
            # Вычисляем viral score
            viral_score = 0
            if view_count > 0:
                engagement = ((like_count + comment_count) / view_count) * 100
                viral_score = round(engagement, 2)
            
            # Формируем объект видео
            description = data.get('description', '') or ''
            tags = data.get('tags') or []
            categories = data.get('categories') or []
            
            # Обработка thumbnail (может быть строкой или списком)
            thumbnail = ''
            thumb_data = data.get('thumbnail') or data.get('thumbnails')
            if isinstance(thumb_data, str):
                thumbnail = thumb_data
            elif isinstance(thumb_data, list) and len(thumb_data) > 0:
                # Берем последнюю (обычно самое высокое разрешение)
                thumbnail = thumb_data[-1].get('url', '') if isinstance(thumb_data[-1], dict) else ''
            
            video = {
                'id': video_id,
                'title': data.get('title', 'Без названия'),
                'description': description[:200] + '...' if description and len(description) > 200 else (description or 'Описание отсутствует'),
                'channel': {
                    'name': data.get('uploader') or data.get('channel') or 'Неизвестный канал',
                    'avatar': data.get('uploader_url', ''),
                    'subscribers': data.get('subscriber_count', 0) or 0
                },
                'thumbnail': thumbnail,
                'views': view_count,
                'likes': like_count,
                'comments': comment_count,
                'duration': data.get('duration', 0) or 0,
                'published_date': data.get('upload_date', ''),
                'platform': 'youtube',
                'viral_score': viral_score,
                'url': f"https://youtube.com/watch?v={video_id}",
                'tags': tags[:5] if isinstance(tags, list) else [],
                'category': categories[0] if (isinstance(categories, list) and len(categories) > 0) else '',
                'language': data.get('language', 'unknown')
            }
            
            return video
            
        except Exception as e:
            import traceback
            logger.error(f"Ошибка парсинга видео: {e}")
            logger.debug(f"Данные видео: {data}")
            logger.debug(traceback.format_exc())
            return None
    
    def search_videos(self, platform: str, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Универсальный поиск видео по платформе"""
        if platform == 'youtube' or platform == 'all':
            return self.search_youtube(query, max_results)
        elif platform == 'instagram':
            logger.warning("Поиск в Instagram требует дополнительной настройки")
            return []
        elif platform == 'tiktok':
            logger.warning("Поиск в TikTok требует дополнительной настройки")
            return []
        else:
            logger.warning(f"Неподдерживаемая платформа: {platform}")
            return []
    
    def apply_filters(self, videos: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Применение фильтров к результатам поиска"""
        filtered = []
        
        for video in videos:
            # Фильтр по просмотрам
            min_views = filters.get('min_views', 0)
            max_views = filters.get('max_views', float('inf'))
            if not (min_views <= video['views'] <= max_views):
                continue
            
            # Фильтр по лайкам
            min_likes = filters.get('min_likes', 0)
            if video['likes'] < min_likes:
                continue
            
            # Фильтр по длительности
            duration_min = filters.get('duration_min', 0)
            duration_max = filters.get('duration_max', float('inf'))
            if not (duration_min <= video['duration'] <= duration_max):
                continue
            
            # Фильтр по engagement
            min_engagement = filters.get('min_engagement', 0)
            if video['viral_score'] < min_engagement:
                continue
            
            # Исключение ключевых слов
            exclude_keywords = filters.get('exclude_keywords', [])
            if any(kw.lower() in video['title'].lower() for kw in exclude_keywords):
                continue
            
            filtered.append(video)
        
        return filtered
