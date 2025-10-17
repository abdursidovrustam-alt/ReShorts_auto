#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Video Downloader - Модуль скачивания видео
Поддерживаемые платформы: TikTok, YouTube, Instagram
"""

import os
import yt_dlp
import requests
from pathlib import Path
import hashlib
from urllib.parse import urlparse
from loguru import logger
import json
import time
from datetime import datetime

class VideoDownloader:
    """Класс для скачивания видео с различных платформ"""
    
    def __init__(self, config):
        self.config = config
        self.download_dir = Path(config.get('paths', {}).get('downloads', './downloads'))
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Настройка HTTP сессии"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session.headers.update(headers)
        
        # Настройка прокси
        proxy_config = self.config.get('proxy', {})
        if proxy_config.get('enabled', False):
            proxies = {
                'http': proxy_config.get('http_proxy'),
                'https': proxy_config.get('https_proxy')
            }
            self.session.proxies.update(proxies)
    
    def download_video(self, video_url, custom_filename=None):
        """Основной метод скачивания видео"""
        logger.info(f"Начало скачивания: {video_url}")
        
        try:
            platform = self._detect_platform(video_url)
            logger.info(f"Определена платформа: {platform}")
            
            if platform == 'tiktok':
                return self._download_tiktok(video_url, custom_filename)
            elif platform == 'youtube':
                return self._download_youtube(video_url, custom_filename)
            elif platform == 'instagram':
                return self._download_instagram(video_url, custom_filename)
            else:
                # Пробуем скачать через yt-dlp
                return self._download_with_ytdlp(video_url, custom_filename)
                
        except Exception as e:
            logger.error(f"Ошибка скачивания {video_url}: {e}")
            return None
    
    def _detect_platform(self, url):
        """Определение платформы по URL"""
        domain = urlparse(url).netloc.lower()
        
        if 'tiktok.com' in domain:
            return 'tiktok'
        elif 'youtube.com' in domain or 'youtu.be' in domain:
            return 'youtube'
        elif 'instagram.com' in domain:
            return 'instagram'
        else:
            return 'unknown'
    
    def _download_tiktok(self, video_url, custom_filename=None):
        """Скачивание TikTok видео"""
        try:
            # Настройки для yt-dlp
            ydl_opts = {
                'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
                'format': 'best[height<=720]',
                'writeinfojson': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'ignoreerrors': True,
                'no_warnings': True,
                'extractaudio': False,
                'audioformat': 'mp3',
                'embed_thumbnail': True,
                'writethumbnail': True
            }
            
            # Прокси для yt-dlp
            proxy_config = self.config.get('proxy', {})
            if proxy_config.get('enabled', False):
                ydl_opts['proxy'] = proxy_config.get('http_proxy')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Получаем информацию о видео
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'unknown')
                
                # Очищаем имя файла
                safe_title = self._sanitize_filename(title)
                filename = custom_filename or f"tiktok_{safe_title}_{int(time.time())}.mp4"
                
                output_path = self.download_dir / filename
                ydl_opts['outtmpl'] = str(output_path.with_suffix(''))
                
                # Скачиваем
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    ydl2.download([video_url])
                
                # Поиск скачанного файла
                video_file = self._find_downloaded_file(safe_title)
                
                if video_file and video_file.exists():
                    logger.info(f"TikTok видео скачано: {video_file}")
                    return str(video_file)
                else:
                    logger.error("Не удалось найти скачанный TikTok файл")
                    return None
                    
        except Exception as e:
            logger.error(f"Ошибка скачивания TikTok: {e}")
            return None
    
    def _download_youtube(self, video_url, custom_filename=None):
        """Скачивание YouTube видео"""
        try:
            ydl_opts = {
                'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
                'format': 'best[height<=720]/best[height<=480]/best',
                'writeinfojson': True,
                'ignoreerrors': True,
                'no_warnings': True,
                'extractaudio': False,
                'embed_thumbnail': True,
                'writethumbnail': True
            }
            
            proxy_config = self.config.get('proxy', {})
            if proxy_config.get('enabled', False):
                ydl_opts['proxy'] = proxy_config.get('http_proxy')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'unknown')
                duration = info.get('duration', 0)
                
                # Проверяем длительность (для Shorts)
                max_duration = self.config.get('video_processing', {}).get('max_duration', 60)
                if duration > max_duration:
                    logger.warning(f"Видео слишком длинное: {duration} сек, макс: {max_duration}")
                
                safe_title = self._sanitize_filename(title)
                filename = custom_filename or f"youtube_{safe_title}_{int(time.time())}.mp4"
                
                output_path = self.download_dir / filename
                ydl_opts['outtmpl'] = str(output_path.with_suffix(''))
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    ydl2.download([video_url])
                
                video_file = self._find_downloaded_file(safe_title)
                
                if video_file and video_file.exists():
                    logger.info(f"YouTube видео скачано: {video_file}")
                    return str(video_file)
                else:
                    logger.error("Не удалось найти скачанный YouTube файл")
                    return None
                    
        except Exception as e:
            logger.error(f"Ошибка скачивания YouTube: {e}")
            return None
    
    def _download_instagram(self, video_url, custom_filename=None):
        """Скачивание Instagram видео"""
        try:
            # Instagram требует специальной обработки
            ydl_opts = {
                'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
                'format': 'best',
                'writeinfojson': True,
                'ignoreerrors': True,
                'no_warnings': True,
                'cookiefile': 'instagram_cookies.txt',  # Можно добавить cookies
            }
            
            proxy_config = self.config.get('proxy', {})
            if proxy_config.get('enabled', False):
                ydl_opts['proxy'] = proxy_config.get('http_proxy')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'unknown')
                
                safe_title = self._sanitize_filename(title)
                filename = custom_filename or f"instagram_{safe_title}_{int(time.time())}.mp4"
                
                output_path = self.download_dir / filename
                ydl_opts['outtmpl'] = str(output_path.with_suffix(''))
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    ydl2.download([video_url])
                
                video_file = self._find_downloaded_file(safe_title)
                
                if video_file and video_file.exists():
                    logger.info(f"Instagram видео скачано: {video_file}")
                    return str(video_file)
                else:
                    logger.error("Не удалось найти скачанный Instagram файл")
                    return None
                    
        except Exception as e:
            logger.error(f"Ошибка скачивания Instagram: {e}")
            return None
    
    def _download_with_ytdlp(self, video_url, custom_filename=None):
        """Универсальное скачивание через yt-dlp"""
        try:
            ydl_opts = {
                'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
                'format': 'best[height<=720]/best',
                'writeinfojson': True,
                'ignoreerrors': True,
                'no_warnings': True,
            }
            
            proxy_config = self.config.get('proxy', {})
            if proxy_config.get('enabled', False):
                ydl_opts['proxy'] = proxy_config.get('http_proxy')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'unknown')
                
                safe_title = self._sanitize_filename(title)
                filename = custom_filename or f"video_{safe_title}_{int(time.time())}.mp4"
                
                output_path = self.download_dir / filename
                ydl_opts['outtmpl'] = str(output_path.with_suffix(''))
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    ydl2.download([video_url])
                
                video_file = self._find_downloaded_file(safe_title)
                
                if video_file and video_file.exists():
                    logger.info(f"Видео скачано: {video_file}")
                    return str(video_file)
                else:
                    logger.error("Не удалось найти скачанный файл")
                    return None
                    
        except Exception as e:
            logger.error(f"Ошибка универсального скачивания: {e}")
            return None
    
    def _sanitize_filename(self, filename):
        """Очистка имени файла от недопустимых символов"""
        # Удаляем недопустимые символы
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Ограничиваем длину
        if len(filename) > 100:
            filename = filename[:100]
        
        # Удаляем пробелы в начале и конце
        filename = filename.strip()
        
        # Заменяем пробелы на подчеркивания
        filename = filename.replace(' ', '_')
        
        return filename
    
    def _find_downloaded_file(self, title_part):
        """Поиск скачанного файла"""
        # Ищем файлы с расширениями видео
        video_extensions = ['.mp4', '.webm', '.mkv', '.avi', '.mov']
        
        for ext in video_extensions:
            # Поиск по части имени
            for file_path in self.download_dir.glob(f"*{title_part[:20]}*{ext}"):
                if file_path.is_file():
                    return file_path
            
            # Поиск по времени создания (последние 5 минут)
            current_time = time.time()
            for file_path in self.download_dir.glob(f"*{ext}"):
                if file_path.is_file() and (current_time - file_path.stat().st_mtime) < 300:  # 5 минут
                    return file_path
        
        return None
    
    def get_video_info(self, video_url):
        """Получение информации о видео без скачивания"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': len(info.get('formats', [])),
                    'upload_date': info.get('upload_date', ''),
                    'webpage_url': info.get('webpage_url', video_url)
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения информации о видео: {e}")
            return None
    
    def batch_download(self, video_urls, progress_callback=None):
        """Пакетное скачивание видео"""
        results = []
        total = len(video_urls)
        
        logger.info(f"Начало пакетного скачивания {total} видео")
        
        for i, url in enumerate(video_urls):
            try:
                if progress_callback:
                    progress_callback(i, total, f"Скачивание {i+1}/{total}")
                
                file_path = self.download_video(url)
                
                if file_path:
                    results.append({
                        'url': url,
                        'file_path': file_path,
                        'success': True,
                        'error': None
                    })
                else:
                    results.append({
                        'url': url,
                        'file_path': None,
                        'success': False,
                        'error': 'Не удалось скачать'
                    })
                
                # Пауза между скачиваниями
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Ошибка пакетного скачивания {url}: {e}")
                results.append({
                    'url': url,
                    'file_path': None,
                    'success': False,
                    'error': str(e)
                })
        
        successful = len([r for r in results if r['success']])
        logger.info(f"Пакетное скачивание завершено. Успешно: {successful}/{total}")
        
        return results
    
    def clean_old_downloads(self, max_age_hours=24):
        """Очистка старых скачанных файлов"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            deleted_count = 0
            
            for file_path in self.download_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Удален старый файл: {file_path.name}")
            
            logger.info(f"Очистка завершена. Удалено {deleted_count} файлов")
            
        except Exception as e:
            logger.error(f"Ошибка очистки: {e}")