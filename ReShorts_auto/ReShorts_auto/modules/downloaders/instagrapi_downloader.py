"""Загрузчик для Instagram на основе Instagrapi"""

import logging
import os
import time
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class InstagrapiDownloader:
    """Загрузчик Instagram с использованием Instagrapi"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "Instagrapi"
        self.supported_platforms = ['instagram']
        self.download_path = config.get('download', {}).get('path', 'downloads')
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Инициализация Instagrapi клиента"""
        try:
            from instagrapi import Client
            
            self.client = Client()
            # Используем анонимный доступ (без логина)
            # Или можно добавить login в конфиге
            logger.info("✅ Instagrapi клиент инициализирован")
        except ImportError:
            logger.error("❌ Instagrapi не установлен. Установите: pip install instagrapi")
            raise
    
    def download(self, url: str) -> Dict[str, Any]:
        """
        Скачивание видео с Instagram
        
        Args:
            url: URL поста/рилса Instagram
            
        Returns:
            Информация о скачанном видео
        """
        try:
            # Извлечение media_pk из URL
            media_pk = self._extract_media_pk(url)
            
            if not media_pk:
                return {'success': False, 'error': 'Не удалось извлечь media_pk из URL'}
            
            # Получение информации о медиа
            media_info = self.client.media_info(media_pk)
            
            # Скачивание видео
            video_path = self.client.video_download(media_pk, folder=self.download_path)
            
            return {
                'success': True,
                'file_path': str(video_path),
                'title': media_info.caption_text if media_info.caption_text else 'Instagram Video',
                'duration': media_info.video_duration if hasattr(media_info, 'video_duration') else 0,
                'views': media_info.view_count if hasattr(media_info, 'view_count') else 0,
                'likes': media_info.like_count,
                'url': url,
                'platform': 'instagram',
                'thumbnail': media_info.thumbnail_url,
                'uploader': media_info.user.username,
                'upload_date': media_info.taken_at.strftime('%Y%m%d') if hasattr(media_info, 'taken_at') else ''
            }
            
        except Exception as e:
            logger.error(f"Ошибка Instagrapi: {e}")
            return {'success': False, 'error': str(e), 'url': url}
    
    def _extract_media_pk(self, url: str) -> Optional[str]:
        """Извлечение media_pk из URL Instagram"""
        try:
            # Используем встроенный метод Instagrapi
            return self.client.media_pk_from_url(url)
        except:
            return None
    
    def supports_platform(self, platform: str) -> bool:
        """Проверка поддержки платформы"""
        return platform in self.supported_platforms
    
    def test_connection(self) -> bool:
        """Тест работоспособности"""
        try:
            return self.client is not None
        except:
            return False
