#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для управления платформами и публикацией контента

Автор: MiniMax Agent
Дата: 2025-10-17
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class PlatformManager:
    """
    Класс для управления публикацией на различные платформы
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_keys = config.get('api_keys', {})
        self.platform_settings = config.get('platforms', {})
        
        # Путь к сохраненным видео
        self.output_dir = Path(config.get('output', {}).get('directory', 'output'))
        
        logger.info("🌐 Менеджер платформ инициализирован")
    
    def publish_to_platform(self, video_path: str, platform: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Публикация видео на заданную платформу
        
        Args:
            video_path: Путь к видео файлу
            platform: Платформа (youtube, tiktok, instagram)
            metadata: Метаданные для публикации
        
        Returns:
            Результат публикации
        """
        logger.info(f"📤 Публикация на {platform}: {Path(video_path).name}")
        
        if not self._is_platform_enabled(platform):
            return {
                'status': 'error',
                'message': f'Платформа {platform} отключена в конфигурации'
            }
        
        try:
            if platform == 'youtube':
                return self._publish_to_youtube(video_path, metadata)
            elif platform == 'tiktok':
                return self._publish_to_tiktok(video_path, metadata)
            elif platform == 'instagram':
                return self._publish_to_instagram(video_path, metadata)
            else:
                return {
                    'status': 'error',
                    'message': f'Неподдерживаемая платформа: {platform}'
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка публикации на {platform}: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка публикации: {str(e)}'
            }
    
    def _is_platform_enabled(self, platform: str) -> bool:
        """
        Проверка, включена ли платформа
        """
        return self.platform_settings.get(platform, {}).get('enabled', False)
    
    def _publish_to_youtube(self, video_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Публикация на YouTube
        """
        # В реальной версии здесь будет YouTube Data API
        logger.info("📺 Публикация на YouTube (демо)")
        
        # Имитация успешной публикации
        return {
            'status': 'success',
            'platform': 'youtube',
            'video_id': f"youtube_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'url': f"https://www.youtube.com/watch?v=demo_{metadata.get('title', '')}",
            'title': metadata.get('title', ''),
            'description': metadata.get('description', ''),
            'published_at': datetime.now().isoformat(),
            'privacy_status': metadata.get('privacy', 'public'),
            'note': 'Демо версия - реальная публикация требует настройки YouTube API'
        }
    
    def _publish_to_tiktok(self, video_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Публикация на TikTok
        """
        logger.info("🎥 Публикация на TikTok (демо)")
        
        return {
            'status': 'success',
            'platform': 'tiktok',
            'video_id': f"tiktok_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'url': f"https://www.tiktok.com/@user/video/demo_{metadata.get('title', '')}",
            'caption': metadata.get('caption', metadata.get('title', '')),
            'hashtags': metadata.get('hashtags', []),
            'published_at': datetime.now().isoformat(),
            'note': 'Демо версия - реальная публикация требует настройки TikTok API'
        }
    
    def _publish_to_instagram(self, video_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Публикация на Instagram
        """
        logger.info("📷 Публикация на Instagram (демо)")
        
        return {
            'status': 'success',
            'platform': 'instagram',
            'media_id': f"instagram_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'url': f"https://www.instagram.com/reel/demo_{metadata.get('title', '')}",
            'caption': metadata.get('caption', metadata.get('title', '')),
            'hashtags': metadata.get('hashtags', []),
            'published_at': datetime.now().isoformat(),
            'note': 'Демо версия - реальная публикация требует настройки Instagram API'
        }
    
    def batch_publish(self, videos: List[Dict[str, Any]], platforms: List[str]) -> Dict[str, Any]:
        """
        Пакетная публикация на несколько платформ
        
        Args:
            videos: Список видео для публикации
            platforms: Список платформ
        
        Returns:
            Сводные результаты публикации
        """
        logger.info(f"📦 Пакетная публикация: {len(videos)} видео на {len(platforms)} платформ")
        
        results = {
            'total_videos': len(videos),
            'total_platforms': len(platforms),
            'publications': [],
            'summary': {
                'successful': 0,
                'failed': 0,
                'skipped': 0
            }
        }
        
        for video in videos:
            video_results = []
            
            for platform in platforms:
                if not self._is_platform_enabled(platform):
                    result = {
                        'video_id': video.get('id'),
                        'platform': platform,
                        'status': 'skipped',
                        'message': f'Платформа {platform} отключена'
                    }
                    results['summary']['skipped'] += 1
                else:
                    metadata = self._prepare_metadata(video, platform)
                    result = self.publish_to_platform(video.get('processed_file', ''), platform, metadata)
                    
                    if result.get('status') == 'success':
                        results['summary']['successful'] += 1
                    else:
                        results['summary']['failed'] += 1
                
                video_results.append(result)
            
            results['publications'].append({
                'video': video,
                'platform_results': video_results
            })
        
        logger.info(f"✅ Пакетная публикация завершена: {results['summary']}")
        return results
    
    def _prepare_metadata(self, video: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
        Подготовка метаданных для конкретной платформы
        """
        base_metadata = {
            'title': video.get('title', ''),
            'description': video.get('description', ''),
            'theme': video.get('theme', ''),
            'original_platform': video.get('platform', '')
        }
        
        # Платформо-специфичные настройки
        if platform == 'youtube':
            base_metadata.update({
                'privacy': 'public',
                'category': '22',  # People & Blogs
                'tags': [base_metadata['theme'], 'shorts', 'вирусное']
            })
        elif platform == 'tiktok':
            base_metadata.update({
                'caption': f"{base_metadata['title']} #{base_metadata['theme']} #viral #shorts",
                'hashtags': [base_metadata['theme'], 'viral', 'shorts', 'fyp']
            })
        elif platform == 'instagram':
            base_metadata.update({
                'caption': f"{base_metadata['title']} #{base_metadata['theme']} #reels #viral",
                'hashtags': [base_metadata['theme'], 'reels', 'viral', 'instagram']
            })
        
        return base_metadata
    
    def schedule_publication(self, videos: List[Dict[str, Any]], platforms: List[str], 
                           schedule_time: datetime) -> Dict[str, Any]:
        """
        Планирование публикации на определенное время
        
        Args:
            videos: Список видео
            platforms: Список платформ
            schedule_time: Время публикации
        
        Returns:
            Информация о запланированной публикации
        """
        logger.info(f"📅 Планирование публикации на {schedule_time}")
        
        # В реальной версии здесь будет система планировщика
        schedule_id = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            'schedule_id': schedule_id,
            'scheduled_time': schedule_time.isoformat(),
            'videos_count': len(videos),
            'platforms': platforms,
            'status': 'scheduled',
            'created_at': datetime.now().isoformat(),
            'note': 'Демо версия - реальное планирование требует настройки cron/scheduler'
        }
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """
        Получение статистики по платформам
        """
        return {
            'enabled_platforms': [p for p, config in self.platform_settings.items() if config.get('enabled', False)],
            'total_platforms': len(self.platform_settings),
            'platform_details': self.platform_settings,
            'last_update': datetime.now().isoformat()
        }