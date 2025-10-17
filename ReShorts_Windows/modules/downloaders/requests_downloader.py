"""
Загрузчик на основе requests для прямых ссылок на видео
Поддерживает: прямые ссылки на MP4, WEBM и другие видеофайлы
Адаптировано под Windows

Автор: MiniMax Agent
Дата: 2025-10-17
"""

import logging
import os
import requests
from typing import Dict, Any
from pathlib import Path
from urllib.parse import urlparse, unquote
import time
import mimetypes

logger = logging.getLogger(__name__)


class RequestsDownloader:
    """Загрузчик на основе requests для прямых ссылок"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "requests"
        self.supported_platforms = ['unknown']  # Для прямых ссылок
        self.download_path = Path(config.get('download', {}).get('path', 'downloads'))
        self.timeout = config.get('download', {}).get('timeout', 60)
        self.max_file_size = config.get('download', {}).get('max_file_size', 100) * 1024 * 1024  # MB в байты
    
    def download(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Скачивание видео через requests
        
        Args:
            url: URL видео
            **kwargs: Дополнительные параметры
            
        Returns:
            Информация о скачанном видео
        """
        try:
            logger.info(f"🔽 Скачивание через requests: {url}")
            
            # Проверка, что это прямая ссылка на видео
            if not self._is_direct_video_url(url):
                return {
                    "success": False,
                    "error": "Не является прямой ссылкой на видео"
                }
            
            # Заголовки для запроса
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Получение информации о файле
            head_response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            
            # Проверка размера файла
            content_length = head_response.headers.get('content-length')
            if content_length:
                file_size = int(content_length)
                if file_size > self.max_file_size:
                    return {
                        "success": False,
                        "error": f"Файл слишком большой: {file_size / 1024 / 1024:.1f} MB"
                    }
            
            # Определение имени файла
            filename = self._get_filename_from_url(url, head_response)
            file_path = self.download_path / filename
            
            # Скачивание файла
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            downloaded_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Проверка размера во время скачивания
                        if downloaded_size > self.max_file_size:
                            f.close()
                            file_path.unlink()  # Удаление частично скачанного файла
                            return {
                                "success": False,
                                "error": "Файл превысил максимальный размер во время скачивания"
                            }
            
            download_time = time.time() - start_time
            
            # Проверка, что файл скачался
            if not file_path.exists() or file_path.stat().st_size == 0:
                return {
                    "success": False,
                    "error": "Файл не скачался или пустой"
                }
            
            # Формирование результата
            result = {
                "success": True,
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "title": file_path.stem,
                "filename": filename,
                "url": url,
                "download_time": download_time,
                "speed": file_path.stat().st_size / download_time if download_time > 0 else 0,
                "content_type": head_response.headers.get('content-type', ''),
                "platform": "direct_link",
                "downloader": self.name
            }
            
            logger.info(f"✅ Успешно скачано: {filename} ({file_path.stat().st_size / 1024 / 1024:.1f} MB)")
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка HTTP запроса: {str(e)}"
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
        Получение информации о файле без скачивания
        
        Args:
            url: URL файла
            
        Returns:
            Информация о файле
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            filename = self._get_filename_from_url(url, response)
            content_length = response.headers.get('content-length')
            
            return {
                "success": True,
                "filename": filename,
                "file_size": int(content_length) if content_length else None,
                "content_type": response.headers.get('content-type', ''),
                "last_modified": response.headers.get('last-modified', ''),
                "url": url,
                "is_video": self._is_video_content_type(response.headers.get('content-type', ''))
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
            # Проверка доступности requests
            test_url = "https://httpbin.org/status/200"
            response = requests.head(test_url, timeout=5)
            
            return {
                "available": response.status_code == 200,
                "error": None
            }
            
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }
    
    def _is_direct_video_url(self, url: str) -> bool:
        """Проверка, является ли URL прямой ссылкой на видео"""
        try:
            # Проверка расширения файла
            parsed_url = urlparse(url)
            path = unquote(parsed_url.path).lower()
            
            video_extensions = ['.mp4', '.webm', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v']
            
            for ext in video_extensions:
                if path.endswith(ext):
                    return True
            
            # Дополнительная проверка через HEAD запрос
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
                content_type = response.headers.get('content-type', '').lower()
                
                return self._is_video_content_type(content_type)
                
            except:
                pass
            
            return False
            
        except Exception:
            return False
    
    def _is_video_content_type(self, content_type: str) -> bool:
        """Проверка, является ли content-type видео"""
        video_types = [
            'video/mp4',
            'video/webm',
            'video/avi',
            'video/quicktime',
            'video/x-msvideo',
            'video/x-flv',
            'video/x-ms-wmv'
        ]
        
        return any(vtype in content_type.lower() for vtype in video_types)
    
    def _get_filename_from_url(self, url: str, response: requests.Response = None) -> str:
        """Получение имени файла из URL или заголовков"""
        try:
            # Попытка получить имя из заголовка Content-Disposition
            if response and 'content-disposition' in response.headers:
                content_disposition = response.headers['content-disposition']
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"\'')
                    return self._sanitize_filename(filename)
            
            # Получение имени из URL
            parsed_url = urlparse(url)
            path = unquote(parsed_url.path)
            filename = os.path.basename(path)
            
            if filename and '.' in filename:
                return self._sanitize_filename(filename)
            
            # Генерация имени по умолчанию
            timestamp = int(time.time())
            
            # Попытка определить расширение по content-type
            if response:
                content_type = response.headers.get('content-type', '')
                extension = mimetypes.guess_extension(content_type.split(';')[0])
                if extension:
                    return f"video_{timestamp}{extension}"
            
            return f"video_{timestamp}.mp4"
            
        except Exception:
            timestamp = int(time.time())
            return f"video_{timestamp}.mp4"
    
    def _sanitize_filename(self, filename: str) -> str:
        """Очистка имени файла для Windows"""
        if not filename:
            return f"video_{int(time.time())}.mp4"
        
        # Удаление запрещенных символов для Windows
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Удаление точек в конце (проблема Windows)
        filename = filename.rstrip('.')
        
        # Ограничение длины
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = name[:100-len(ext)] + ext
        
        return filename.strip() or f"video_{int(time.time())}.mp4"