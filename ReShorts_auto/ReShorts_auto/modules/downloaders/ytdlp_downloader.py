"""Загрузчик на основе yt-dlp
Поддерживает: YouTube, TikTok, Facebook, Twitter и 1000+ других платформ
"""

import logging
import os
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class YTDLPDownloader:
    """Загрузчик на основе yt-dlp"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "yt-dlp"
        self.supported_platforms = ['youtube', 'tiktok', 'facebook', 'twitter', 'unknown']
        self.download_path = config.get('download', {}).get('path', 'downloads')
        self._init_ytdlp()
    
    def _init_ytdlp(self):
        """Инициализация yt-dlp"""
        try:
            import yt_dlp
            self.yt_dlp = yt_dlp
            logger.info("✅ yt-dlp инициализирован")
        except ImportError:
            logger.error("❌ yt-dlp не установлен. Установите: pip install yt-dlp")
            raise
    
    def download(self, url: str) -> Dict[str, Any]:
        """
        Скачивание видео через yt-dlp
        
        Args:
            url: URL видео
            
        Returns:
            Информация о скачанном видео
        """
        try:
            # Настройки yt-dlp
            download_config = self.config.get('download', {})
            
            ydl_opts = {
                'format': self._get_format_string(download_config.get('video_quality', 'best')),
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
            }
            
            # Субтитры
            if download_config.get('subtitles'):
                ydl_opts['writesubtitles'] = True
                ydl_opts['writeautomaticsub'] = True
            
            # Превью
            if download_config.get('thumbnail', True):
                ydl_opts['writethumbnail'] = True
            
            # Прокси
            if download_config.get('proxy', {}).get('enabled'):
                ydl_opts['proxy'] = download_config['proxy'].get('url')
            
            # Скачивание
            with self.yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if info:
                    video_file = ydl.prepare_filename(info)
                    
                    return {
                        'success': True,
                        'file_path': video_file,
                        'title': info.get('title', ''),
                        'duration': info.get('duration', 0),
                        'views': info.get('view_count', 0),
                        'likes': info.get('like_count', 0),
                        'url': url,
                        'platform': info.get('extractor', ''),
                        'thumbnail': info.get('thumbnail', ''),
                        'description': info.get('description', ''),
                        'uploader': info.get('uploader', ''),
                        'upload_date': info.get('upload_date', '')
                    }
            
            return {'success': False, 'error': 'Не удалось извлечь информацию'}
            
        except Exception as e:
            logger.error(f"Ошибка yt-dlp: {e}")
            return {'success': False, 'error': str(e), 'url': url}
    
    def _get_format_string(self, quality: str) -> str:
        """Получение строки формата для yt-dlp"""
        format_map = {
            'best': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '1080p': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]',
            '720p': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]',
            '480p': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]'
        }
        return format_map.get(quality, format_map['best'])
    
    def supports_platform(self, platform: str) -> bool:
        """Проверка поддержки платформы"""
        return platform in self.supported_platforms
    
    def test_connection(self) -> bool:
        """Тест работоспособности"""
        try:
            # Простая проверка импорта
            import yt_dlp
            return True
        except:
            return False
