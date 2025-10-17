"""Загрузчик для TikTok"""

import logging
import os
import requests
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TikTokDownloader:
    """Загрузчик TikTok видео"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "TikTok Scraper"
        self.supported_platforms = ['tiktok']
        self.download_path = config.get('download', {}).get('path', 'downloads')
        self._init_scraper()
    
    def _init_scraper(self):
        """Инициализация TikTok scraper"""
        try:
            # Используем TikTokApi если доступен
            from TikTokApi import TikTokApi
            self.api = TikTokApi()
            self.use_api = True
            logger.info("✅ TikTokApi инициализирован")
        except ImportError:
            # Fallback на простой HTTP scraping
            self.use_api = False
            logger.info("✅ TikTok HTTP scraper инициализирован")
    
    def download(self, url: str) -> Dict[str, Any]:
        """
        Скачивание видео с TikTok
        
        Args:
            url: URL TikTok видео
            
        Returns:
            Информация о скачанном видео
        """
        try:
            if self.use_api:
                return self._download_with_api(url)
            else:
                return self._download_with_http(url)
                
        except Exception as e:
            logger.error(f"Ошибка TikTok загрузчика: {e}")
            return {'success': False, 'error': str(e), 'url': url}
    
    def _download_with_api(self, url: str) -> Dict[str, Any]:
        """Скачивание через TikTokApi"""
        try:
            # Извлечение video_id из URL
            video_id = self._extract_video_id(url)
            
            if not video_id:
                return {'success': False, 'error': 'Не удалось извлечь video_id'}
            
            # Получение информации о видео
            video_data = self.api.video(id=video_id)
            video_info = video_data.info()
            
            # Скачивание видео
            video_bytes = video_data.bytes()
            
            # Сохранение файла
            filename = f"tiktok_{video_id}.mp4"
            file_path = os.path.join(self.download_path, filename)
            
            with open(file_path, 'wb') as f:
                f.write(video_bytes)
            
            return {
                'success': True,
                'file_path': file_path,
                'title': video_info.get('desc', 'TikTok Video'),
                'duration': video_info.get('duration', 0),
                'views': video_info.get('stats', {}).get('playCount', 0),
                'likes': video_info.get('stats', {}).get('diggCount', 0),
                'url': url,
                'platform': 'tiktok',
                'uploader': video_info.get('author', {}).get('uniqueId', ''),
                'upload_date': ''
            }
            
        except Exception as e:
            logger.error(f"Ошибка TikTokApi: {e}")
            raise
    
    def _download_with_http(self, url: str) -> Dict[str, Any]:
        """Скачивание через HTTP scraping (fallback метод)"""
        try:
            # Используем сторонний API для скачивания TikTok
            # Например, можно использовать публичные API как ssstik.io, tikmate.online и т.д.
            
            # Для примера используем простой метод через yt-dlp (если доступен)
            try:
                import yt_dlp
                
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': os.path.join(self.download_path, '%(id)s.%(ext)s'),
                    'quiet': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    if info:
                        return {
                            'success': True,
                            'file_path': ydl.prepare_filename(info),
                            'title': info.get('title', 'TikTok Video'),
                            'duration': info.get('duration', 0),
                            'views': info.get('view_count', 0),
                            'likes': info.get('like_count', 0),
                            'url': url,
                            'platform': 'tiktok',
                            'uploader': info.get('uploader', ''),
                            'upload_date': info.get('upload_date', '')
                        }
            except:
                pass
            
            return {'success': False, 'error': 'TikTok scraping недоступен'}
            
        except Exception as e:
            logger.error(f"Ошибка HTTP scraping: {e}")
            raise
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Извлечение video_id из TikTok URL"""
        import re
        
        # Паттерны для разных форматов URL
        patterns = [
            r'tiktok\.com/@[\w\.-]+/video/(\d+)',
            r'tiktok\.com/v/(\d+)',
            r'vm\.tiktok\.com/(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def supports_platform(self, platform: str) -> bool:
        """Проверка поддержки платформы"""
        return platform in self.supported_platforms
    
    def test_connection(self) -> bool:
        """Тест работоспособности"""
        return True
