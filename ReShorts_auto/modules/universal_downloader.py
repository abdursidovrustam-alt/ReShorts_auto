"""
Универсальный модуль скачивания видео без API
Поддержка: YouTube (yt-dlp), Instagram (instagrapi), TikTok (TikTok scraper)
Автоматический fallback между методами
"""

import logging
import os
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class UniversalDownloader:
    """Универсальный загрузчик видео с поддержкой нескольких методов"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.download_path = config.get('download', {}).get('path', 'downloads')
        self.downloaders = []
        
        # Создание папки для загрузок
        Path(self.download_path).mkdir(parents=True, exist_ok=True)
        
        # Инициализация загрузчиков
        self._init_downloaders()
    
    def _init_downloaders(self):
        """Инициализация доступных загрузчиков"""
        download_config = self.config.get('download', {})
        methods = download_config.get('methods', {})
        
        # yt-dlp (YouTube, TikTok и другие)
        if methods.get('ytdlp', {}).get('enabled', True):
            try:
                from .downloaders.ytdlp_downloader import YTDLPDownloader
                self.downloaders.append(YTDLPDownloader(self.config))
                logger.info("✅ yt-dlp загрузчик инициализирован")
            except Exception as e:
                logger.warning(f"⚠️ yt-dlp недоступен: {e}")
        
        # Instagrapi (Instagram)
        if methods.get('instagrapi', {}).get('enabled', True):
            try:
                from .downloaders.instagrapi_downloader import InstagrapiDownloader
                self.downloaders.append(InstagrapiDownloader(self.config))
                logger.info("✅ Instagrapi загрузчик инициализирован")
            except Exception as e:
                logger.warning(f"⚠️ Instagrapi недоступен: {e}")
        
        # TikTok Scraper
        if methods.get('tiktok', {}).get('enabled', True):
            try:
                from .downloaders.tiktok_downloader import TikTokDownloader
                self.downloaders.append(TikTokDownloader(self.config))
                logger.info("✅ TikTok загрузчик инициализирован")
            except Exception as e:
                logger.warning(f"⚠️ TikTok загрузчик недоступен: {e}")
        
        if not self.downloaders:
            logger.error("❌ Ни один загрузчик не доступен!")
            raise RuntimeError("Нет доступных загрузчиков")
        
        logger.info(f"📊 Инициализировано {len(self.downloaders)} загрузчиков")
    
    def download_video(self, url: str, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Скачивание видео с автоматическим выбором метода
        
        Args:
            url: URL видео
            platform: Платформа (youtube, instagram, tiktok) или None для автоопределения
            
        Returns:
            Информация о скачанном видео
        """
        # Определение платформы
        if not platform:
            platform = self._detect_platform(url)
        
        logger.info(f"📥 Скачивание с {platform}: {url}")
        
        # Попытка скачать с fallback
        max_retries = self.config.get('download', {}).get('max_retries', 3)
        
        for attempt in range(max_retries):
            for downloader in self.downloaders:
                # Проверка, поддерживает ли загрузчик эту платформу
                if not downloader.supports_platform(platform):
                    continue
                
                try:
                    logger.info(f"🔄 Попытка {attempt + 1}/{max_retries} с {downloader.name}")
                    
                    result = downloader.download(url)
                    
                    if result and result.get('success'):
                        logger.info(f"✅ Успешно скачано через {downloader.name}")
                        return result
                    
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка с {downloader.name}: {e}")
                    continue
            
            # Пауза перед следующей попыткой
            if attempt < max_retries - 1:
                time.sleep(2)
        
        logger.error(f"❌ Не удалось скачать видео: {url}")
        return {
            "success": False,
            "error": "Все методы скачивания не сработали",
            "url": url
        }
    
    def download_batch(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Пакетное скачивание видео
        
        Args:
            urls: Список URL для скачивания
            
        Returns:
            Список результатов
        """
        results = []
        
        for i, url in enumerate(urls, 1):
            logger.info(f"📦 Скачивание {i}/{len(urls)}")
            result = self.download_video(url)
            results.append(result)
            
            # Небольшая пауза между скачиваниями
            if i < len(urls):
                time.sleep(1)
        
        successful = sum(1 for r in results if r.get('success'))
        logger.info(f"✅ Успешно скачано: {successful}/{len(urls)}")
        
        return results
    
    def _detect_platform(self, url: str) -> str:
        """Определение платформы по URL"""
        url_lower = url.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
            return 'facebook'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        else:
            return 'unknown'
    
    def get_downloader_status(self) -> List[Dict[str, Any]]:
        """Получение статуса всех загрузчиков"""
        status = []
        for downloader in self.downloaders:
            try:
                is_available = downloader.test_connection()
                status.append({
                    "name": downloader.name,
                    "available": is_available,
                    "platforms": downloader.supported_platforms,
                    "priority": self.downloaders.index(downloader) + 1
                })
            except:
                status.append({
                    "name": downloader.name,
                    "available": False,
                    "platforms": [],
                    "priority": self.downloaders.index(downloader) + 1
                })
        return status


class BaseDownloader:
    """Базовый класс для загрузчиков"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "BaseDownloader"
        self.supported_platforms = []
    
    def download(self, url: str) -> Dict[str, Any]:
        """Скачивание видео"""
        raise NotImplementedError
    
    def supports_platform(self, platform: str) -> bool:
        """Проверка поддержки платформы"""
        return platform in self.supported_platforms
    
    def test_connection(self) -> bool:
        """Тест работоспособности загрузчика"""
        return True
