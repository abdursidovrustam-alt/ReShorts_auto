#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReShorts Windows - Главный файл backend приложения
Система для поиска, анализа и создания вирусных коротких видео без API ключей
Адаптировано под Windows

Автор: MiniMax Agent
Дата: 2025-10-17
"""

import os
import sys
import json
import time
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path, WindowsPath
import hashlib
import random
import uuid

from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

# Обеспечиваем совместимость с Windows
if os.name == 'nt':  # Windows
    import ctypes
    ctypes.windll.kernel32.SetConsoleCP(65001)
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)

# Импорт модулей
from modules.universal_downloader import UniversalDownloader
from modules.video_search import VideoSearchEngine
from ai_analyzer.multi_provider import AIProviderManager

# Настройка логирования для Windows
def setup_logging():
    """Настройка системы логирования с поддержкой Windows"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Форматтер с поддержкой UTF-8
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Файловый обработчик
    file_handler = logging.FileHandler(
        log_dir / 'reshorts.log', 
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Настройка корневого логгера
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )

setup_logging()
logger = logging.getLogger(__name__)


class ReShortsApp:
    def __init__(self):
        """Инициализация главного класса приложения"""
        self.app = Flask(__name__, 
                        static_folder='web_interface',
                        static_url_path='',
                        template_folder='web_interface')
        
        # Настройка CORS
        CORS(self.app, origins=["*"])
        
        # Загрузка конфигурации
        self.config = self.load_config()
        
        # Инициализация компонентов
        self.stats = self.load_stats()
        self.downloader = UniversalDownloader(self.config)
        self.search_engine = VideoSearchEngine(self.config)
        self.ai_manager = AIProviderManager(self.config)
        
        # Создание необходимых директорий
        self.create_directories()
        
        # Регистрация маршрутов
        self.register_routes()
        
        logger.info("✅ ReShorts приложение инициализировано")
    
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из файла"""
        try:
            config_path = Path('config.json')
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info("✅ Конфигурация загружена")
                return config
            else:
                logger.warning("⚠️ Файл config.json не найден, используется базовая конфигурация")
                return self.get_default_config()
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфигурации: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Базовая конфигурация по умолчанию"""
        return {
            "search": {
                "max_results": 10,
                "min_views": 1000,
                "min_engagement": 2.0
            },
            "download": {
                "path": "downloads",
                "max_retries": 3
            },
            "ai": {
                "timeout": 30,
                "max_retries": 3
            }
        }
    
    def load_stats(self) -> Dict[str, Any]:
        """Загрузка статистики"""
        try:
            stats_path = Path('logs/stats.json')
            if stats_path.exists():
                with open(stats_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ Ошибка загрузки статистики: {e}")
        
        return {
            "downloaded": 0,
            "analyzed": 0,
            "processed": 0,
            "success_rate": 0,
            "activity_log": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def save_stats(self):
        """Сохранение статистики"""
        try:
            stats_path = Path('logs/stats.json')
            stats_path.parent.mkdir(exist_ok=True)
            
            self.stats["last_updated"] = datetime.now().isoformat()
            
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения статистики: {e}")
    
    def create_directories(self):
        """Создание необходимых директорий"""
        dirs = ['downloads', 'processed', 'logs', 'tmp', 'output']
        for dir_name in dirs:
            Path(dir_name).mkdir(exist_ok=True)
        logger.info("✅ Директории созданы")
    
    def register_routes(self):
        """Регистрация всех маршрутов API"""
        
        # Главная страница
        @self.app.route('/')
        def index():
            return send_from_directory('web_interface', 'index.html')
        
        # API статистики
        @self.app.route('/api/stats')
        def get_stats():
            """Получение статистики системы"""
            try:
                chart_data = self._get_activity_chart_data()
                recent_operations = self.stats.get('activity_log', [])[-10:]
                
                return jsonify({
                    "status": "success",
                    "data": {
                        "downloaded": self.stats.get('downloaded', 0),
                        "analyzed": self.stats.get('analyzed', 0),
                        "processed": self.stats.get('processed', 0),
                        "success_rate": self.stats.get('success_rate', 0),
                        "chart_data": chart_data,
                        "recent_operations": recent_operations
                    }
                })
            except Exception as e:
                logger.error(f"❌ Ошибка получения статистики: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
        
        # API поиска видео
        @self.app.route('/api/search', methods=['POST'])
        def search_videos():
            """Поиск видео с расширенными фильтрами"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"status": "error", "message": "Нет данных запроса"}), 400
                
                # Выполнение поиска
                results = self.search_engine.search(data)
                
                # Логирование операции
                self._log_activity('search', f"Найдено {len(results)} видео")
                
                return jsonify({
                    "status": "success",
                    "data": results,
                    "count": len(results)
                })
                
            except Exception as e:
                error_msg = f"Ошибка поиска: {str(e)}"
                logger.error(f"❌ {error_msg}")
                logger.error(traceback.format_exc())
                return jsonify({"status": "error", "message": error_msg}), 500
        
        # API скачивания видео
        @self.app.route('/api/download', methods=['POST'])
        def download_video():
            """Скачивание видео"""
            try:
                data = request.get_json()
                if not data or 'url' not in data:
                    return jsonify({"status": "error", "message": "URL не указан"}), 400
                
                url = data['url']
                result = self.downloader.download(url)
                
                if result.get('success'):
                    self.stats['downloaded'] += 1
                    self._log_activity('download', f"Скачано: {result.get('title', 'Неизвестно')}")
                    self.save_stats()
                
                return jsonify({
                    "status": "success" if result.get('success') else "error",
                    "data": result
                })
                
            except Exception as e:
                error_msg = f"Ошибка скачивания: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return jsonify({"status": "error", "message": error_msg}), 500
        
        # API анализа видео
        @self.app.route('/api/analyze', methods=['POST'])
        def analyze_video():
            """AI анализ видео"""
            try:
                data = request.get_json()
                if not data or 'video_data' not in data:
                    return jsonify({"status": "error", "message": "Данные видео не указаны"}), 400
                
                video_data = data['video_data']
                prompt = data.get('prompt', self.config.get('ai', {}).get('default_prompt', ''))
                
                # Выполнение анализа
                result = self.ai_manager.analyze(video_data, prompt)
                
                if result.get('success'):
                    self.stats['analyzed'] += 1
                    self._log_activity('analyze', "Анализ выполнен")
                    self.save_stats()
                
                return jsonify({
                    "status": "success" if result.get('success') else "error",
                    "data": result
                })
                
            except Exception as e:
                error_msg = f"Ошибка анализа: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return jsonify({"status": "error", "message": error_msg}), 500
        
        # API управления файлами
        @self.app.route('/api/files')
        def get_files():
            """Получение списка файлов"""
            try:
                files_info = []
                downloads_dir = Path(self.config.get('download', {}).get('path', 'downloads'))
                
                if downloads_dir.exists():
                    for file_path in downloads_dir.iterdir():
                        if file_path.is_file():
                            stat = file_path.stat()
                            files_info.append({
                                "name": file_path.name,
                                "size": stat.st_size,
                                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                                "path": str(file_path)
                            })
                
                return jsonify({
                    "status": "success",
                    "data": files_info
                })
                
            except Exception as e:
                error_msg = f"Ошибка получения файлов: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return jsonify({"status": "error", "message": error_msg}), 500
        
        # API настроек
        @self.app.route('/api/config')
        def get_config():
            """Получение конфигурации"""
            return jsonify({
                "status": "success",
                "data": self.config
            })
        
        @self.app.route('/api/config', methods=['POST'])
        def update_config():
            """Обновление конфигурации"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"status": "error", "message": "Нет данных"}), 400
                
                # Обновление конфигурации
                self.config.update(data)
                
                # Сохранение в файл
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                
                logger.info("✅ Конфигурация обновлена")
                return jsonify({"status": "success", "message": "Конфигурация сохранена"})
                
            except Exception as e:
                error_msg = f"Ошибка сохранения конфигурации: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return jsonify({"status": "error", "message": error_msg}), 500
        
        # API статуса системы
        @self.app.route('/api/system-status')
        def get_system_status():
            """Получение статуса системы"""
            try:
                import psutil
                
                # Информация о системе
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('.')
                
                # Статус компонентов
                downloaders_status = self.downloader.get_status()
                ai_providers_status = self.ai_manager.get_status()
                
                return jsonify({
                    "status": "success",
                    "data": {
                        "system": {
                            "cpu_percent": cpu_percent,
                            "memory_percent": memory.percent,
                            "disk_percent": (disk.used / disk.total) * 100,
                            "uptime": time.time() - self.start_time if hasattr(self, 'start_time') else 0
                        },
                        "downloaders": downloaders_status,
                        "ai_providers": ai_providers_status
                    }
                })
                
            except Exception as e:
                error_msg = f"Ошибка получения статуса: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return jsonify({"status": "error", "message": error_msg}), 500
    
    def _log_activity(self, activity_type: str, description: str):
        """Логирование активности"""
        activity = {
            "id": str(uuid.uuid4()),
            "type": activity_type,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        
        if 'activity_log' not in self.stats:
            self.stats['activity_log'] = []
        
        self.stats['activity_log'].append(activity)
        
        # Оставляем только последние 100 записей
        if len(self.stats['activity_log']) > 100:
            self.stats['activity_log'] = self.stats['activity_log'][-100:]
    
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
            searches = sum(1 for a in day_activities if a.get('type') == 'search')
            
            chart_data.append({
                "date": date_str,
                "downloads": downloads,
                "analyzes": analyzes,
                "searches": searches,
                "total": downloads + analyzes + searches
            })
        
        return chart_data
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Запуск приложения"""
        self.start_time = time.time()
        logger.info(f"🚀 Запуск ReShorts на http://{host}:{port}")
        logger.info(f"💻 Операционная система: {os.name}")
        logger.info(f"📁 Рабочая директория: {os.getcwd()}")
        
        try:
            self.app.run(host=host, port=port, debug=debug, threaded=True)
        except Exception as e:
            logger.error(f"❌ Ошибка запуска приложения: {e}")
            raise


def main():
    """Точка входа в приложение"""
    try:
        print("=" * 60)
        print("🎬 ReShorts Windows - Запуск системы")
        print("=" * 60)
        
        app = ReShortsApp()
        app.run(host='127.0.0.1', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n⛔ Остановка по запросу пользователя")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        traceback.print_exc()
        input("Нажмите Enter для закрытия...")


if __name__ == '__main__':
    main()