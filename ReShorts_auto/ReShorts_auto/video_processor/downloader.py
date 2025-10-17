import os
import logging
from pathlib import Path
import yt_dlp

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoDownloader:
    """
    Класс для загрузки видео с YouTube используя yt-dlp с cookies для обхода bot detection
    """
    
    def __init__(self, cookies_file=None):
        """
        Args:
            cookies_file (str): Путь к файлу с cookies (по умолчанию 'cookies.txt')
        """
        self.cookies_file = cookies_file or 'cookies.txt'
        logger.info(f"Инициализация VideoDownloader (cookies: {self.cookies_file})")
    
    def download_video(self, video_url, output_path='downloads', quality='highest'):
        """
        Загружает видео по URL используя yt-dlp с cookies для обхода блокировки
        
        Args:
            video_url (str): URL видео на YouTube
            output_path (str): Путь для сохранения видео (папка или полный путь к файлу)
            quality (str): Качество видео ('highest', '720p', '480p', '360p', '144p')
            
        Returns:
            dict: Информация о скачанном видео
                {
                    'success': bool,
                    'file_path': str,
                    'title': str,
                    'duration': int,
                    'error': str (если есть ошибка)
                }
        """
        try:
            print("📡 Подключение к YouTube через yt-dlp...")
            
            # Создаем директорию если её нет
            if not output_path.endswith('.mp4'):
                Path(output_path).mkdir(parents=True, exist_ok=True)
                output_template = os.path.join(output_path, '%(title)s.%(ext)s')
            else:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                output_template = output_path
            
            # Определяем формат
            if quality == 'highest':
                format_str = 'best[ext=mp4]'
            else:
                # Для указанного качества выбираем соответствующий формат
                height = quality.replace('p', '')
                format_str = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]'
            
            # Настройки yt-dlp
            ydl_opts = {
                'format': format_str,
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
                'extractor_args': 'youtube:player_client=ios,web',  # Используем iOS и web клиенты
            }
            
            # Добавляем cookies если файл существует
            if os.path.exists(self.cookies_file):
                ydl_opts['cookiefile'] = self.cookies_file
                print(f"🍪 Использую cookies из файла: {self.cookies_file}")
            else:
                print(f"⚠️  Внимание: файл cookies не найден ({self.cookies_file})")
                print("   Загрузка может не работать из-за блокировки YouTube bot detection")
            
            print(f"🔄 Начало загрузки видео...")
            
            # Загружаем видео
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                
                # Проверяем, что info - это словарь
                if not isinstance(info, dict):
                    raise ValueError(f"Неожиданный тип результата: {type(info)}")
                
                file_path = ydl.prepare_filename(info)
            
            if file_path and os.path.exists(file_path):
                print(f"✅ Видео успешно загружено!")
                print(f"📺 Название: {info.get('title', 'N/A')}")
                print(f"💾 Файл: {file_path}")
                
                return {
                    'success': True,
                    'file_path': file_path,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'video_id': info.get('id', ''),
                    'view_count': info.get('view_count', 0),
                    'resolution': f"{info.get('width', 0)}x{info.get('height', 0)}",
                    'filesize_mb': info.get('filesize', 0) / (1024*1024) if info.get('filesize') else 0
                }
            else:
                error_msg = "Не удалось найти загруженный файл"
                print(f"❌ {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'file_path': None
                }
            
        except Exception as e:
            error_msg = f"Ошибка при загрузке видео: {str(e)}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'file_path': None
            }
    
    def download_multiple_videos(self, video_urls, output_path='downloads', quality='highest'):
        """
        Скачивает несколько видео
        
        Args:
            video_urls (list): Список URL видео
            output_path (str): Путь для сохранения видео
            quality (str): Качество видео
            
        Returns:
            list: Список результатов для каждого видео
        """
        results = []
        for i, url in enumerate(video_urls, 1):
            print(f"\n{'='*50}")
            print(f"[{i}/{len(video_urls)}] Обработка видео {i}")
            print(f"{'='*50}")
            result = self.download_video(url, output_path, quality)
            results.append(result)
        
        return results


def download_video(video_url, output_path='downloads', quality='highest', cookies_file=None):
    """
    Удобная функция для быстрого скачивания одного видео
    
    Args:
        video_url (str): URL видео для скачивания
        output_path (str): Путь для сохранения видео
        quality (str): Качество видео
        cookies_file (str): Путь к файлу cookies (опционально)
        
    Returns:
        dict: Информация о скачанном видео
    """
    downloader = VideoDownloader(cookies_file=cookies_file)
    return downloader.download_video(video_url, output_path, quality)
