#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReShorts - Главный файл backend приложения
Система для поиска, анализа и создания вирусных коротких видео без API ключей

Автор: MiniMax Agent
Дата: 2025-10-17
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib
import random

from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

# Импорт новых модулей
from modules.universal_downloader import UniversalDownloader
import importlib
import sys
# Принудительная перезагрузка модуля video_search
if 'modules.video_search' in sys.modules:
    importlib.reload(sys.modules['modules.video_search'])
from modules.video_search import VideoSearchEngine
from ai_analyzer.multi_provider import AIProviderManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/reshorts.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ReShortsApp:
    def __init__(self):
        """Инициализация главного класса приложения"""
        self.app = Flask(__name__, 
                        static_folder='web_interface',
                        template_folder='web_interface')
        
        # Настройка CORS
        CORS(self.app)
        
        # Создание необходимых папок
        self.create_directories()
        
        # Загрузка конфигурации
        self.config = self.load_config()
        
        # Инициализация модулей
        self.downloader = None
        self.ai_manager = None
        self.search_engine = None
        self.init_modules()
        
        # Хранилище для пресетов фильтров
        self.filter_presets = self.load_filter_presets()
        
        # Хранилище для статистики
        self.stats = self.load_stats()
        
        # Регистрация маршрутов
        self.register_routes()
        
        logger.info("✅ ReShorts приложение инициализировано")
    
    def create_directories(self):
        """Создание необходимых директорий"""
        dirs = ['downloads', 'logs', 'output', 'processed', 'tmp', 'data']
        for dir_name in dirs:
            Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из файла"""
        config_path = 'config.json'
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info("✅ Конфигурация загружена из config.json")
                return config
            except Exception as e:
                logger.error(f"❌ Ошибка загрузки config.json: {e}")
        
        # Конфигурация по умолчанию
        return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Получение конфигурации по умолчанию"""
        return {
            "search": {
                "queries": ["#viral", "trending"],
                "max_results": 10,
                "date_range": "this_week",
                "min_views": 1000,
                "min_engagement": 5.0
            },
            "ai": {
                "providers": {
                    "gpt4free": {"enabled": True},
                    "openrouter": {"enabled": True},
                    "gemini": {"enabled": True},
                    "localai": {"enabled": False}
                },
                "timeout": 30,
                "max_retries": 3,
                "cache_enabled": True
            },
            "download": {
                "methods": {
                    "ytdlp": {"enabled": True},
                    "instagrapi": {"enabled": True},
                    "tiktok": {"enabled": True}
                },
                "video_quality": "best",
                "max_file_size": 100,
                "path": "downloads",
                "subtitles": False,
                "thumbnail": True,
                "proxy": {
                    "enabled": False,
                    "url": ""
                }
            },
            "processing": {
                "clip_duration": 30,
                "clips_per_video": 3,
                "output_format": "mp4",
                "video_bitrate": 2500,
                "auto_crop": True,
                "add_watermark": False,
                "filter_duplicates": True,
                "filter_low_quality": True,
                "exclude_keywords": []
            },
            "scenarios": {
                "auto_search": True,
                "auto_download": True,
                "auto_analyze": True,
                "auto_process": False,
                "auto_run_interval": 60,
                "notify_on_complete": True,
                "notify_on_error": True
            }
        }
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Сохранение конфигурации в файл"""
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.config = config
            logger.info("✅ Конфигурация сохранена")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения конфигурации: {e}")
            return False
    
    def load_filter_presets(self) -> List[Dict[str, Any]]:
        """Загрузка сохраненных пресетов фильтров"""
        presets_file = 'data/filter_presets.json'
        if os.path.exists(presets_file):
            try:
                with open(presets_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Ошибка загрузки пресетов: {e}")
        return []
    
    def save_filter_presets(self, presets: List[Dict[str, Any]]) -> bool:
        """Сохранение пресетов фильтров"""
        try:
            with open('data/filter_presets.json', 'w', encoding='utf-8') as f:
                json.dump(presets, f, indent=2, ensure_ascii=False)
            self.filter_presets = presets
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения пресетов: {e}")
            return False
    
    def load_stats(self) -> Dict[str, Any]:
        """Загрузка статистики"""
        stats_file = 'data/stats.json'
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Ошибка загрузки статистики: {e}")
        return {
            "total_downloaded": 0,
            "total_analyzed": 0,
            "total_processed": 0,
            "success_rate": 0,
            "activity_log": []
        }
    
    def save_stats(self, stats: Dict[str, Any]) -> bool:
        """Сохранение статистики"""
        try:
            with open('data/stats.json', 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            self.stats = stats
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения статистики: {e}")
            return False
    
    def update_stats(self, event_type: str, success: bool = True):
        """Обновление статистики"""
        if event_type == "download":
            self.stats["total_downloaded"] += 1
        elif event_type == "analyze":
            self.stats["total_analyzed"] += 1
        elif event_type == "process":
            self.stats["total_processed"] += 1
        
        # Добавление в лог активности
        activity = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "success": success
        }
        
        self.stats.setdefault("activity_log", []).insert(0, activity)
        
        # Ограничение лога до 100 записей
        if len(self.stats["activity_log"]) > 100:
            self.stats["activity_log"] = self.stats["activity_log"][:100]
        
        # Пересчет процента успеха
        total_operations = sum(1 for a in self.stats["activity_log"])
        successful_operations = sum(1 for a in self.stats["activity_log"] if a.get("success"))
        if total_operations > 0:
            self.stats["success_rate"] = round((successful_operations / total_operations) * 100, 1)
        
        self.save_stats(self.stats)
    
    def init_modules(self):
        """Инициализация основных модулей"""
        # Инициализация загрузчика видео (необязательно)
        try:
            self.downloader = UniversalDownloader(self.config)
            logger.info("✅ Загрузчик инициализирован")
        except Exception as e:
            logger.warning(f"⚠️ Загрузчик недоступен: {e}")
            self.downloader = None
        
        # Инициализация AI менеджера (необязательно)
        try:
            self.ai_manager = AIProviderManager(self.config)
            logger.info("✅ AI менеджер инициализирован")
        except Exception as e:
            logger.warning(f"⚠️ AI менеджер недоступен: {e}")
            self.ai_manager = None
        
        # Инициализация поисковика видео (обязательно)
        try:
            self.search_engine = VideoSearchEngine(self.config)
            logger.info("✅ Поисковик видео инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации поисковика: {e}")
            self.search_engine = None
    
    def register_routes(self):
        """Регистрация всех маршрутов приложения"""
        
        # ===== Статические страницы =====
        @self.app.route('/')
        def index():
            """Главная страница"""
            return render_template('index.html')
        
        @self.app.route('/settings')
        def settings():
            """Страница настроек"""
            return render_template('settings.html')
        
        # ===== API для конфигурации =====
        @self.app.route('/api/config/get', methods=['GET'])
        def get_config():
            """Получение текущей конфигурации"""
            try:
                return jsonify(self.config), 200
            except Exception as e:
                logger.error(f"Ошибка получения конфигурации: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/config/save', methods=['POST'])
        def save_config_api():
            """Сохранение конфигурации"""
            try:
                new_config = request.json
                
                if not new_config:
                    return jsonify({"error": "Пустая конфигурация"}), 400
                
                success = self.save_config(new_config)
                
                if success:
                    # Переинициализация модулей с новой конфигурацией
                    self.init_modules()
                    return jsonify({"success": True, "message": "Конфигурация сохранена"}), 200
                else:
                    return jsonify({"error": "Ошибка сохранения"}), 500
                    
            except Exception as e:
                logger.error(f"Ошибка сохранения конфигурации: {e}")
                return jsonify({"error": str(e)}), 500
        
        # ===== API для поиска и предпросмотра =====
        @self.app.route('/api/search/preview', methods=['POST'])
        def search_preview():
            """Поиск видео с расширенными фильтрами"""
            try:
                data = request.json
                platform = data.get('platform', 'all')
                query = data.get('query', '')
                
                # Фильтры
                min_views = data.get('min_views', 0)
                max_views = data.get('max_views', float('inf'))
                min_likes = data.get('min_likes', 0)
                duration_min = data.get('duration_min', 0)
                duration_max = data.get('duration_max', float('inf'))
                date_range = data.get('date_range', 'all')
                language = data.get('language', 'any')
                min_engagement = data.get('min_engagement', 0)
                exclude_keywords = data.get('exclude_keywords', [])
                
                logger.info(f"🔍 Поиск видео: platform={platform}, query={query}")
                
                # Реальный поиск видео через VideoSearchEngine
                if self.search_engine:
                    videos = self.search_engine.search_videos(platform, query, max_results=20)
                    # Применение фильтров
                    filtered_videos = self.search_engine.apply_filters(videos, data)
                else:
                    # Fallback на мок-данные если поисковик не инициализирован
                    logger.warning("Поисковик не инициализирован, используются мок-данные")
                    videos = self._generate_mock_videos(query, platform, 20)
                    # Применение фильтров
                    filtered_videos = []
                    for video in videos:
                        # Фильтрация по просмотрам
                        if not (min_views <= video['views'] <= max_views):
                            continue
                        
                        # Фильтрация по лайкам
                        if video['likes'] < min_likes:
                            continue
                        
                        # Фильтрация по длительности
                        if not (duration_min <= video['duration'] <= duration_max):
                            continue
                        
                        # Фильтрация по engagement
                        if video['viral_score'] < min_engagement:
                            continue
                        
                        # Исключение ключевых слов
                        if any(kw.lower() in video['title'].lower() for kw in exclude_keywords):
                            continue
                        
                        filtered_videos.append(video)
                
                return jsonify({
                    "success": True,
                    "total": len(filtered_videos),
                    "videos": filtered_videos
                }), 200
                
            except Exception as e:
                logger.error(f"Ошибка поиска: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/video/details/<video_id>', methods=['GET'])
        def get_video_details(video_id):
            """Получение детальной информации о видео"""
            try:
                logger.info(f"📹 Запрос деталей видео: {video_id}")
                
                # В реальном приложении здесь будет запрос к API платформы
                # Для демонстрации генерируем детали
                details = self._generate_video_details(video_id)
                
                return jsonify(details), 200
                
            except Exception as e:
                logger.error(f"Ошибка получения деталей: {e}")
                return jsonify({"error": str(e)}), 500
        
        # ===== API для пресетов фильтров =====
        @self.app.route('/api/filters/save', methods=['POST'])
        def save_filter_preset():
            """Сохранение пресета фильтров"""
            try:
                data = request.json
                name = data.get('name')
                filters = data.get('filters')
                
                if not name or not filters:
                    return jsonify({"error": "Название и фильтры обязательны"}), 400
                
                # Создание нового пресета
                preset = {
                    "id": hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:8],
                    "name": name,
                    "filters": filters,
                    "created_at": datetime.now().isoformat()
                }
                
                # Добавление в список
                self.filter_presets.append(preset)
                self.save_filter_presets(self.filter_presets)
                
                logger.info(f"💾 Сохранен пресет фильтров: {name}")
                
                return jsonify({
                    "success": True,
                    "preset": preset
                }), 200
                
            except Exception as e:
                logger.error(f"Ошибка сохранения пресета: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/filters/list', methods=['GET'])
        def list_filter_presets():
            """Получение списка сохраненных пресетов"""
            try:
                return jsonify({
                    "success": True,
                    "presets": self.filter_presets
                }), 200
            except Exception as e:
                logger.error(f"Ошибка получения пресетов: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/filters/delete/<preset_id>', methods=['DELETE'])
        def delete_filter_preset(preset_id):
            """Удаление пресета фильтров"""
            try:
                self.filter_presets = [p for p in self.filter_presets if p['id'] != preset_id]
                self.save_filter_presets(self.filter_presets)
                
                return jsonify({"success": True}), 200
            except Exception as e:
                logger.error(f"Ошибка удаления пресета: {e}")
                return jsonify({"error": str(e)}), 500
        
        # ===== API для статистики дашборда =====
        @self.app.route('/api/stats/dashboard', methods=['GET'])
        def get_dashboard_stats():
            """Получение статистики для дашборда"""
            try:
                # Статистика за последние 7 дней
                activity_chart = self._get_activity_chart_data()
                
                # Последние операции
                recent_operations = self.stats.get('activity_log', [])[:10]
                
                dashboard_data = {
                    "stats": {
                        "total_downloaded": self.stats.get('total_downloaded', 0),
                        "total_analyzed": self.stats.get('total_analyzed', 0),
                        "total_processed": self.stats.get('total_processed', 0),
                        "success_rate": self.stats.get('success_rate', 0)
                    },
                    "activity_chart": activity_chart,
                    "recent_operations": recent_operations
                }
                
                return jsonify(dashboard_data), 200
                
            except Exception as e:
                logger.error(f"Ошибка получения статистики: {e}")
                return jsonify({"error": str(e)}), 500
        
        # ===== API для скачивания видео =====
        @self.app.route('/api/download', methods=['POST'])
        def download_video():
            """Скачивание одного видео"""
            try:
                data = request.json
                url = data.get('url')
                platform = data.get('platform')
                
                if not url:
                    return jsonify({"error": "URL не указан"}), 400
                
                logger.info(f"📥 Запрос на скачивание: {url}")
                
                result = self.downloader.download_video(url, platform)
                
                # Обновление статистики
                self.update_stats("download", result.get('success', False))
                
                return jsonify(result), 200
                
            except Exception as e:
                logger.error(f"Ошибка скачивания: {e}")
                self.update_stats("download", False)
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/download/batch', methods=['POST'])
        def download_batch():
            """Пакетное скачивание видео"""
            try:
                data = request.json
                urls = data.get('urls', [])
                
                if not urls:
                    return jsonify({"error": "Список URL пуст"}), 400
                
                logger.info(f"📥 Пакетное скачивание: {len(urls)} видео")
                
                results = self.downloader.download_batch(urls)
                
                return jsonify({"results": results}), 200
                
            except Exception as e:
                logger.error(f"Ошибка пакетного скачивания: {e}")
                return jsonify({"error": str(e)}), 500
        
        # ===== API для AI анализа =====
        @self.app.route('/api/analyze', methods=['POST'])
        def analyze_video():
            """Анализ видео с помощью AI"""
            try:
                data = request.json
                video_data = data.get('video_data')
                prompt = data.get('prompt')
                
                if not video_data:
                    return jsonify({"error": "Данные видео не предоставлены"}), 400
                
                logger.info("🤖 Запрос на AI анализ")
                
                result = self.ai_manager.analyze_video(video_data, prompt)
                
                # Обновление статистики
                self.update_stats("analyze", result.get('success', False))
                
                return jsonify(result), 200
                
            except Exception as e:
                logger.error(f"Ошибка AI анализа: {e}")
                self.update_stats("analyze", False)
                return jsonify({"error": str(e)}), 500
        
        # ===== API для статуса системы =====
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Получение статуса всех модулей"""
            try:
                status = {
                    "downloaders": self.downloader.get_downloader_status() if self.downloader else [],
                    "ai_providers": self.ai_manager.get_provider_status() if self.ai_manager else [],
                    "timestamp": datetime.now().isoformat()
                }
                
                return jsonify(status), 200
                
            except Exception as e:
                logger.error(f"Ошибка получения статуса: {e}")
                return jsonify({"error": str(e)}), 500
        
        # ===== API для работы с файлами =====
        @self.app.route('/api/files/list', methods=['GET'])
        def list_files():
            """Список скачанных файлов"""
            try:
                download_path = self.config.get('download', {}).get('path', 'downloads')
                
                if not os.path.exists(download_path):
                    return jsonify({"files": []}), 200
                
                files = []
                for filename in os.listdir(download_path):
                    filepath = os.path.join(download_path, filename)
                    if os.path.isfile(filepath):
                        files.append({
                            "name": filename,
                            "size": os.path.getsize(filepath),
                            "modified": os.path.getmtime(filepath)
                        })
                
                return jsonify({"files": files}), 200
                
            except Exception as e:
                logger.error(f"Ошибка получения списка файлов: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/files/delete/<filename>', methods=['DELETE'])
        def delete_file(filename):
            """Удаление файла"""
            try:
                download_path = self.config.get('download', {}).get('path', 'downloads')
                filepath = os.path.join(download_path, filename)
                
                if os.path.exists(filepath):
                    os.remove(filepath)
                    return jsonify({"success": True, "message": f"Файл {filename} удален"}), 200
                else:
                    return jsonify({"error": "Файл не найден"}), 404
                    
            except Exception as e:
                logger.error(f"Ошибка удаления файла: {e}")
                return jsonify({"error": str(e)}), 500
        
        # ===== Статические файлы =====
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            """Обслуживание статических файлов"""
            return send_from_directory('web_interface', filename)
    
    def _generate_mock_videos(self, query: str, platform: str, count: int) -> List[Dict[str, Any]]:
        """Генерация мок-данных видео для демонстрации"""
        videos = []
        platforms = ['youtube', 'instagram', 'tiktok'] if platform == 'all' else [platform]
        
        titles = [
            "Как стать популярным в 2025",
            "Лучшие лайфхаки для соцсетей",
            "ТОП-10 трендов этого месяца",
            "Секреты вирусных видео",
            "Невероятные факты о TikTok",
            "Как собрать миллион подписчиков",
            "Лайфхаки для создателей контента",
            "Все о Reels за 5 минут",
            "Тренды YouTube Shorts",
            "История успеха блогера"
        ]
        
        channels = [
            "Вирусные Тренды",
            "TikTok Эксперт",
            "Контент Мастер",
            "Social Media Pro",
            "Блогер 2.0"
        ]
        
        for i in range(count):
            video_platform = random.choice(platforms)
            video_id = hashlib.md5(f"{query}{i}{time.time()}".encode()).hexdigest()[:12]
            
            views = random.randint(10000, 5000000)
            likes = int(views * random.uniform(0.03, 0.15))
            comments = int(views * random.uniform(0.001, 0.01))
            engagement = ((likes + comments) / views) * 100 if views > 0 else 0
            
            video = {
                "id": video_id,
                "title": f"{random.choice(titles)} | {query}" if query else random.choice(titles),
                "description": f"Описание видео {query}. Узнайте больше о том, как создавать вирусный контент.",
                "channel": {
                    "name": random.choice(channels),
                    "avatar": f"https://i.pravatar.cc/150?u={video_id}",
                    "subscribers": random.randint(10000, 1000000)
                },
                "thumbnail": f"https://picsum.photos/seed/{video_id}/640/360",
                "views": views,
                "likes": likes,
                "comments": comments,
                "duration": random.randint(15, 180),
                "published_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "platform": video_platform,
                "viral_score": round(engagement, 2),
                "url": f"https://{video_platform}.com/watch/{video_id}"
            }
            
            videos.append(video)
        
        return videos
    
    def _generate_video_details(self, video_id: str) -> Dict[str, Any]:
        """Генерация детальной информации о видео"""
        views = random.randint(50000, 10000000)
        likes = int(views * random.uniform(0.05, 0.15))
        
        return {
            "id": video_id,
            "title": "Подробный гайд по созданию вирусных видео",
            "description": "В этом видео я расскажу о всех секретах создания вирусного контента. Подписывайтесь и ставьте лайк!",
            "channel": {
                "name": "Вирусные Тренды",
                "avatar": f"https://i.pravatar.cc/150?u={video_id}",
                "subscribers": random.randint(100000, 5000000)
            },
            "thumbnail": f"https://picsum.photos/seed/{video_id}/1280/720",
            "views": views,
            "likes": likes,
            "dislikes": int(likes * random.uniform(0.01, 0.05)),
            "comments": int(views * random.uniform(0.002, 0.01)),
            "duration": random.randint(30, 300),
            "published_date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
            "platform": "youtube",
            "viral_score": round(((likes) / views) * 100, 2) if views > 0 else 0,
            "tags": ["viral", "trending", "shorts", "вирусные", "тренды"],
            "category": "Образование",
            "language": "ru",
            "url": f"https://youtube.com/watch/{video_id}"
        }
    
    def _get_activity_chart_data(self) -> List[Dict[str, Any]]:
        """Получение данных для графика активности за 7 дней"""
        chart_data = []
        activity_log = self.stats.get('activity_log', [])
        
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            date_str = date.strftime("%Y-%m-%d")
            
            # Подсчет операций за этот день
            day_activities = [
                a for a in activity_log 
                if a.get('timestamp', '').startswith(date_str)
            ]
            
            downloads = sum(1 for a in day_activities if a.get('type') == 'download')
            analyzes = sum(1 for a in day_activities if a.get('type') == 'analyze')
            processes = sum(1 for a in day_activities if a.get('type') == 'process')
            
            chart_data.append({
                "date": date_str,
                "downloads": downloads,
                "analyzes": analyzes,
                "processes": processes,
                "total": downloads + analyzes + processes
            })
        
        return chart_data
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Запуск приложения"""
        logger.info(f"🚀 Запуск ReShorts на http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def main():
    """Точка входа в приложение"""
    app = ReShortsApp()
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    main()
