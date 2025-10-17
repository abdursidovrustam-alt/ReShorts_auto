"""
Загрузчик на основе yt-dlp
Поддерживает: YouTube, TikTok, Facebook, Twitter и 1000+ других платформ
Адаптировано под Windows

Автор: MiniMax Agent  
Дата: 2025-10-17
"""

import logging
import os
import time
from typing import Dict, Any
from pathlib import Path
from urllib.parse import urlparse
import json

logger = logging.getLogger(__name__)


class YTDLPDownloader:
    """Загрузчик на основе yt-dlp"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "yt-dlp"
        self.supported_platforms = ['youtube', 'tiktok', 'facebook', 'twitter', 'unknown']
        self.download_path = Path(config.get('download', {}).get('path', 'downloads'))
        self.timeout = config.get('download', {}).get('timeout', 120)
        self._init_ytdlp()
    
    def _init_ytdlp(self):
        """Инициализация yt-dlp"""
        try:
            import yt_dlp
            self.yt_dlp = yt_dlp
            logger.info("✅ yt-dlp инициализирован")
        except ImportError:
            logger.error("❌ yt-dlp не установлен. Установите: pip install yt-dlp")
            raise ImportError("yt-dlp не найден")
    
    def download(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Скачивание видео через yt-dlp
        
        Args:
            url: URL видео
            **kwargs: Дополнительные параметры
            
        Returns:
            Информация о скачанном видео
        """
        try:
            # Настройки yt-dlp
            download_config = self.config.get('download', {})
            
            # Создание безопасного имени файла
            output_template = str(self.download_path / '%(title)s.%(ext)s')
            
            ydl_opts = {
                'format': self._get_format_string(download_config.get('video_quality', 'best')),
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'writethumbnail': download_config.get('thumbnail', True),
                'writesubtitles': download_config.get('subtitles', False),
                'writeinfojson': True,
                'socket_timeout': self.timeout,
                'retries': download_config.get('max_retries', 3),
                # Windows-specific настройки
                'windowsfilenames': True if os.name == 'nt' else False,
                'restrictfilenames': True,
            }
            
            # Обработка прокси
            proxy_config = download_config.get('proxy', {})
            if proxy_config.get('enabled') and proxy_config.get('url'):
                ydl_opts['proxy'] = proxy_config['url']
            
            # Ограничение размера файла
            max_size = download_config.get('max_file_size', 100)  # MB
            if max_size > 0:
                ydl_opts['format'] += f'[filesize<{max_size}M]'
            
            logger.info(f"🔽 Скачивание через yt-dlp: {url}")
            
            with self.yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Сначала получаем информацию
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return {
                        "success": False,
                        "error": "Не удалось получить информацию о видео"
                    }
                
                # Проверка длительности
                duration = info.get('duration', 0)
                duration_max = self.config.get('search', {}).get('duration_max', 600)
                
                if duration > duration_max:
                    return {
                        "success": False,
                        "error": f"Видео слишком длинное ({duration}с > {duration_max}с)"
                    }
                
                # Скачивание
                ydl.download([url])
                
                # Поиск скачанного файла
                title = self._sanitize_filename(info.get('title', 'video'))
                downloaded_file = self._find_downloaded_file(title)
                
                if not downloaded_file:
                    return {
                        "success": False,
                        "error": "Файл не найден после скачивания"
                    }
                
                # Формирование результата
                result = {
                    "success": True,
                    "file_path": str(downloaded_file),
                    "file_size": downloaded_file.stat().st_size,
                    "title": info.get('title', ''),
                    "description": info.get('description', ''),
                    "duration": duration,
                    "view_count": info.get('view_count', 0),
                    "like_count": info.get('like_count', 0),
                    "uploader": info.get('uploader', ''),
                    "upload_date": info.get('upload_date', ''),
                    "url": url,
                    "thumbnail": info.get('thumbnail', ''),
                    "platform": self._detect_platform(url),
                    "downloader": self.name
                }
                
                logger.info(f"✅ Успешно скачано: {title}")
                return result
                
        except self.yt_dlp.DownloadError as e:
            error_msg = f"Ошибка yt-dlp: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Неожиданная ошибка: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_info(self, url: str) -> Dict[str, Any]:
        """
        Получение информации о видео без скачивания
        
        Args:
            url: URL видео
            
        Returns:
            Информация о видео
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'socket_timeout': 30,
            }
            
            with self.yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return {
                        "success": False,
                        "error": "Не удалось получить информацию о видео"
                    }
                
                return {
                    "success": True,
                    "title": info.get('title', ''),
                    "description": info.get('description', ''),
                    "duration": info.get('duration', 0),
                    "view_count": info.get('view_count', 0),
                    "like_count": info.get('like_count', 0),
                    "dislike_count": info.get('dislike_count', 0),
                    "comment_count": info.get('comment_count', 0),
                    "uploader": info.get('uploader', ''),
                    "upload_date": info.get('upload_date', ''),
                    "thumbnail": info.get('thumbnail', ''),
                    "url": url,
                    "platform": self._detect_platform(url)
                }
                
        except Exception as e:
            error_msg = f"Ошибка получения информации: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def check_status(self) -> Dict[str, Any]:
        """Проверка статуса загрузчика"""
        try:
            # Проверка доступности yt-dlp
            if not hasattr(self, 'yt_dlp'):
                return {
                    "available": False,
                    "error": "yt-dlp не инициализирован"
                }
            
            return {
                "available": True,
                "version": getattr(self.yt_dlp, 'version', 'unknown'),
                "error": None
            }
            
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }
    
    def _get_format_string(self, quality: str) -> str:
        """Получение строки формата для yt-dlp"""
        format_map = {
            'worst': 'worst',
            'best': 'best[height<=720]',
            'audio': 'bestaudio',
            '144p': 'worst[height<=144]',
            '240p': 'best[height<=240]',
            '360p': 'best[height<=360]',
            '480p': 'best[height<=480]',
            '720p': 'best[height<=720]',
            '1080p': 'best[height<=1080]'
        }
        
        return format_map.get(quality, 'best[height<=720]')
    
    def _detect_platform(self, url: str) -> str:
        """Определение платформы по URL"""
        url_lower = url.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
            return 'facebook'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        else:
            return 'unknown'
    
    def _sanitize_filename(self, filename: str) -> str:
        """Очистка имени файла для Windows"""
        if not filename:
            return "video"
        
        # Удаление запрещенных символов для Windows
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Удаление точек в конце (проблема Windows)
        filename = filename.rstrip('.')
        
        # Ограничение длины
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename.strip() or "video"
    
    def _find_downloaded_file(self, title_hint: str) -> Path:
        """Поиск скачанного файла"""
        try:
            video_extensions = ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv']
            
            # Поиск файлов в директории загрузок
            for file_path in self.download_path.iterdir():
                if file_path.is_file():
                    # Проверка расширения
                    if file_path.suffix.lower() in video_extensions:
                        # Проверка содержания названия
                        if title_hint.lower() in file_path.stem.lower():
                            return file_path
            
            # Если не найдено по названию, берем последний скачанный видеофайл
            video_files = [
                f for f in self.download_path.iterdir()
                if f.is_file() and f.suffix.lower() in video_extensions
            ]
            
            if video_files:
                # Сортировка по времени создания
                video_files.sort(key=lambda x: x.stat().st_ctime, reverse=True)
                return video_files[0]
            
        except Exception as e:
            logger.error(f"Ошибка поиска файла: {e}")
        
        return None