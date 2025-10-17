"""
Универсальный модуль скачивания видео без API
Поддержка: YouTube (yt-dlp), прямые ссылки
Адаптировано под Windows

Автор: MiniMax Agent
Дата: 2025-10-17
"""

import logging
import os
import time
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path, WindowsPath
import json
import hashlib
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)


class UniversalDownloader:
    """Универсальный загрузчик видео с поддержкой нескольких методов"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.download_path = Path(config.get('download', {}).get('path', 'downloads'))
        self.max_retries = config.get('download', {}).get('max_retries', 3)
        self.timeout = config.get('download', {}).get('timeout', 60)
        
        # Создание папки для загрузок
        self.download_path.mkdir(parents=True, exist_ok=True)
        
        # Инициализация загрузчиков
        self.downloaders = []
        self._init_downloaders()
    
    def _init_downloaders(self):
        """Инициализация доступных загрузчиков"""
        download_config = self.config.get('download', {})
        methods = download_config.get('methods', {})
        
        # yt-dlp (YouTube, TikTok и другие)
        if methods.get('ytdlp', {}).get('enabled', True):
            try:
                from modules.downloaders.ytdlp_downloader import YTDLPDownloader
                downloader = YTDLPDownloader(self.config)
                self.downloaders.append(downloader)
                logger.info("✅ yt-dlp загрузчик инициализирован")
            except Exception as e:
                logger.warning(f"⚠️ yt-dlp недоступен: {e}")
        
        # Requests (прямые ссылки)
        if methods.get('requests', {}).get('enabled', True):
            try:
                from modules.downloaders.requests_downloader import RequestsDownloader
                downloader = RequestsDownloader(self.config)
                self.downloaders.append(downloader)
                logger.info("✅ Requests загрузчик инициализирован")
            except Exception as e:
                logger.warning(f"⚠️ Requests загрузчик недоступен: {e}")
        
        if not self.downloaders:
            logger.error("❌ Нет доступных загрузчиков!")
    
    def download(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Скачивание видео с автоматическим fallback между методами
        
        Args:
            url: URL видео
            **kwargs: Дополнительные параметры
            
        Returns:
            Информация о результате скачивания
        """
        if not url:
            return {
                "success": False,
                "error": "URL не указан",
                "downloader": None
            }
        
        logger.info(f"🔽 Начало скачивания: {url}")
        
        # Определение платформы
        platform = self._detect_platform(url)
        logger.info(f"📱 Обнаружена платформа: {platform}")
        
        # Попытка скачивания через доступные загрузчики
        last_error = None
        for downloader in self.downloaders:
            if platform in downloader.supported_platforms or 'unknown' in downloader.supported_platforms:
                try:
                    logger.info(f"🔄 Попытка скачивания через {downloader.name}")
                    result = downloader.download(url, **kwargs)
                    
                    if result.get('success'):
                        logger.info(f"✅ Успешно скачано через {downloader.name}")
                        result['downloader'] = downloader.name
                        result['platform'] = platform
                        return result
                    else:
                        last_error = result.get('error', 'Неизвестная ошибка')
                        logger.warning(f"⚠️ {downloader.name}: {last_error}")
                        
                except Exception as e:
                    last_error = str(e)
                    logger.error(f"❌ Ошибка в {downloader.name}: {e}")
                    continue
        
        # Если все методы не сработали
        error_msg = f"Не удалось скачать видео. Последняя ошибка: {last_error}"
        logger.error(f"❌ {error_msg}")
        
        return {
            "success": False,
            "error": error_msg,
            "url": url,
            "platform": platform,
            "downloader": None
        }
    
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
    
    def get_download_info(self, url: str) -> Dict[str, Any]:
        """
        Получение информации о видео без скачивания
        
        Args:
            url: URL видео
            
        Returns:
            Информация о видео
        """
        for downloader in self.downloaders:
            if hasattr(downloader, 'get_info'):
                try:
                    info = downloader.get_info(url)
                    if info.get('success'):
                        return info
                except Exception as e:
                    logger.warning(f"Ошибка получения информации через {downloader.name}: {e}")
                    continue
        
        return {
            "success": False,
            "error": "Не удалось получить информацию о видео"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса всех загрузчиков"""
        status = {}
        
        for downloader in self.downloaders:
            try:
                # Проверка доступности загрузчика
                if hasattr(downloader, 'check_status'):
                    downloader_status = downloader.check_status()
                else:
                    downloader_status = {"available": True, "error": None}
                
                status[downloader.name] = {
                    "available": downloader_status.get('available', True),
                    "error": downloader_status.get('error'),
                    "supported_platforms": downloader.supported_platforms
                }
                
            except Exception as e:
                status[downloader.name] = {
                    "available": False,
                    "error": str(e),
                    "supported_platforms": getattr(downloader, 'supported_platforms', [])
                }
        
        return status
    
    def cleanup_downloads(self, older_than_days: int = 7) -> Dict[str, Any]:
        """
        Очистка старых загруженных файлов
        
        Args:
            older_than_days: Удалить файлы старше указанного количества дней
            
        Returns:
            Результат очистки
        """
        try:
            deleted_count = 0
            deleted_size = 0
            cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)
            
            for file_path in self.download_path.iterdir():
                if file_path.is_file():
                    file_stat = file_path.stat()
                    if file_stat.st_mtime < cutoff_time:
                        file_size = file_stat.st_size
                        file_path.unlink()
                        deleted_count += 1
                        deleted_size += file_size
                        logger.info(f"🗑️ Удален старый файл: {file_path.name}")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "deleted_size": deleted_size,
                "message": f"Удалено {deleted_count} файлов ({deleted_size / 1024 / 1024:.1f} MB)"
            }
            
        except Exception as e:
            error_msg = f"Ошибка очистки: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }


def sanitize_filename(filename: str) -> str:
    """Очистка имени файла для Windows"""
    # Удаление запрещенных символов для Windows
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Ограничение длины
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    
    return filename.strip()


def get_file_hash(file_path: Path) -> str:
    """Получение хеша файла для проверки дубликатов"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""