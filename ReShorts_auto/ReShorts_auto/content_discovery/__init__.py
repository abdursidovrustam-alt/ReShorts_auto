#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для поиска вирусного контента на различных платформах

Автор: MiniMax Agent
Дата: 2025-10-17
"""

import requests
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ContentDiscovery:
    """
    Класс для поиска и анализа вирусного контента
    на YouTube, TikTok и Instagram
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_keys = config.get('api_keys', {})
        self.platform_settings = config.get('platforms', {})
        
    def search_viral_content(self, theme: str, platform: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Поиск вирусного контента по заданной тематике
        
        Args:
            theme: Тематика для поиска
            platform: Платформа (youtube, tiktok, instagram)
            limit: Максимальное количество результатов
        
        Returns:
            Список найденных видео с метаданными
        """
        logger.info(f"🔍 Поиск вирусного контента: {theme} на {platform}")
        
        if platform == 'youtube':
            return self._search_youtube(theme, limit)
        elif platform == 'tiktok':
            return self._search_tiktok(theme, limit)
        elif platform == 'instagram':
            return self._search_instagram(theme, limit)
        else:
            raise ValueError(f"Неподдерживаемая платформа: {platform}")
    
    def _search_youtube(self, theme: str, limit: int) -> List[Dict[str, Any]]:
        """
        Поиск на YouTube через YouTube Data API v3
        """
        api_key = self.api_keys.get('youtube_api_key')
        if not api_key:
            logger.warning("YouTube API ключ не найден, возвращаем демо данные")
            return self._generate_demo_results(theme, 'youtube', limit)
        
        try:
            # Поиск видео
            search_url = "https://www.googleapis.com/youtube/v3/search"
            search_params = {
                'key': api_key,
                'part': 'snippet',
                'type': 'video',
                'q': f"{theme} shorts",
                'order': 'viewCount',
                'publishedAfter': (datetime.now() - timedelta(days=30)).isoformat() + 'Z',
                'maxResults': limit,
                'videoDuration': 'short'  # Только короткие видео
            }
            
            response = requests.get(search_url, params=search_params)
            response.raise_for_status()
            search_data = response.json()
            
            # Получение статистики для каждого видео
            video_ids = [item['id']['videoId'] for item in search_data.get('items', [])]
            if not video_ids:
                return []
            
            stats_url = "https://www.googleapis.com/youtube/v3/videos"
            stats_params = {
                'key': api_key,
                'part': 'statistics,contentDetails',
                'id': ','.join(video_ids)
            }
            
            stats_response = requests.get(stats_url, params=stats_params)
            stats_response.raise_for_status()
            stats_data = stats_response.json()
            
            # Объединение данных
            results = []
            for i, item in enumerate(search_data.get('items', [])):
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                # Поиск статистики для этого видео
                stats = next((s['statistics'] for s in stats_data.get('items', []) if s['id'] == video_id), {})
                duration_info = next((s['contentDetails'] for s in stats_data.get('items', []) if s['id'] == video_id), {})
                
                video_data = {
                    'id': video_id,
                    'platform': 'youtube',
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'published_at': snippet.get('publishedAt', ''),
                    'channel': snippet.get('channelTitle', ''),
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comments': int(stats.get('commentCount', 0)),
                    'duration': duration_info.get('duration', ''),
                    'viral_score': self._calculate_viral_score(stats),
                    'theme': theme
                }
                results.append(video_data)
            
            # Сортировка по вирусности
            results.sort(key=lambda x: x['viral_score'], reverse=True)
            
            logger.info(f"✅ Найдено {len(results)} YouTube видео")
            return results
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска на YouTube: {e}")
            return self._generate_demo_results(theme, 'youtube', limit)
    
    def _search_tiktok(self, theme: str, limit: int) -> List[Dict[str, Any]]:
        """
        Поиск на TikTok (демо версия)
        """
        logger.info(f"🔍 Поиск на TikTok: {theme}")
        # В реальной версии здесь будет TikTok API
        return self._generate_demo_results(theme, 'tiktok', limit)
    
    def _search_instagram(self, theme: str, limit: int) -> List[Dict[str, Any]]:
        """
        Поиск на Instagram (демо версия)
        """
        logger.info(f"🔍 Поиск на Instagram: {theme}")
        # В реальной версии здесь будет Instagram Basic Display API
        return self._generate_demo_results(theme, 'instagram', limit)
    
    def _calculate_viral_score(self, stats: Dict[str, Any]) -> float:
        """
        Расчет индекса вирусности на основе статистики
        """
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        
        if views == 0:
            return 0.0
        
        # Простая формула вирусности
        like_ratio = likes / views if views > 0 else 0
        comment_ratio = comments / views if views > 0 else 0
        engagement = like_ratio + comment_ratio * 2  # Комментарии весят больше
        
        # Нормализация (0-1)
        viral_score = min(1.0, engagement * 10)
        
        return round(viral_score, 3)
    
    def _generate_demo_results(self, theme: str, platform: str, limit: int) -> List[Dict[str, Any]]:
        """
        Генерация демо результатов для тестирования
        """
        logger.info(f"📝 Генерация демо результатов для {platform}")
        
        results = []
        for i in range(1, min(limit + 1, 11)):
            video_data = {
                'id': f"{platform}_demo_{i}",
                'platform': platform,
                'title': f"{theme} - Вирусное видео {i}",
                'description': f"Демо описание для видео по теме {theme}",
                'url': f"https://{platform}.com/demo_{i}",
                'thumbnail': f"https://picsum.photos/320/240?random={i}",
                'published_at': (datetime.now() - timedelta(days=i)).isoformat(),
                'channel': f"Канал{i}",
                'views': 50000 + (i * 10000),
                'likes': 5000 + (i * 1000),
                'comments': 500 + (i * 100),
                'duration': f"00:0{min(i + 10, 59)}",
                'viral_score': round(0.7 + (i * 0.02), 3),
                'theme': theme
            }
            results.append(video_data)
        
        return results
    
    def analyze_trends(self, platform: str, days: int = 7) -> Dict[str, Any]:
        """
        Анализ трендов на платформе за указанный период
        """
        logger.info(f"📈 Анализ трендов на {platform} за {days} дней")
        
        # В реальной версии здесь будет анализ трендовых тем
        trending_topics = [
            "мотивация", "лайфхаки", "юмор", "танцы", "готовка",
            "спорт", "красота", "технологии", "путешествия", "музыка"
        ]
        
        return {
            'platform': platform,
            'period_days': days,
            'trending_topics': trending_topics[:5],
            'analysis_date': datetime.now().isoformat()
        }