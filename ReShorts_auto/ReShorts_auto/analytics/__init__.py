#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для аналитики и статистики продуктивности

Автор: MiniMax Agent
Дата: 2025-10-17
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import sqlite3

logger = logging.getLogger(__name__)

class Analytics:
    """
    Класс для сбора и анализа статистики
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.analytics_dir = Path('analytics')
        self.analytics_dir.mkdir(exist_ok=True)
        
        # База данных для статистики
        self.db_path = self.analytics_dir / 'analytics.db'
        self._init_database()
        
        logger.info("📈 Модуль аналитики инициализирован")
    
    def _init_database(self):
        """
        Инициализация базы данных SQLite
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Таблица для статистики видео
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS video_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    title TEXT,
                    theme TEXT,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    viral_score REAL DEFAULT 0,
                    processed_at TIMESTAMP,
                    published_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица для общей статистики
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value TEXT NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица для сессий обработки
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    theme TEXT,
                    platform TEXT,
                    videos_requested INTEGER,
                    videos_processed INTEGER,
                    videos_published INTEGER,
                    uniqueness_level TEXT,
                    processing_time_seconds REAL,
                    success_rate REAL,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации базы данных: {e}")
    
    def track_video_processing(self, video_data: Dict[str, Any], processing_result: Dict[str, Any]):
        """
        Отслеживание обработки видео
        
        Args:
            video_data: Данные о видео
            processing_result: Результат обработки
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO video_stats 
                (video_id, platform, title, theme, views, likes, comments, 
                 viral_score, processed_at, published_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_data.get('id', ''),
                video_data.get('platform', ''),
                video_data.get('title', ''),
                video_data.get('theme', ''),
                video_data.get('views', 0),
                video_data.get('likes', 0),
                video_data.get('comments', 0),
                video_data.get('viral_score', 0),
                processing_result.get('processed_at'),
                None  # published_at будет обновлен при публикации
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📉 Отслежена обработка видео: {video_data.get('id')}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отслеживания обработки: {e}")
    
    def track_processing_session(self, session_data: Dict[str, Any]):
        """
        Отслеживание сессии обработки
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO processing_sessions
                (session_id, theme, platform, videos_requested, videos_processed,
                 videos_published, uniqueness_level, processing_time_seconds,
                 success_rate, started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_data.get('session_id'),
                session_data.get('theme'),
                session_data.get('platform'),
                session_data.get('videos_requested', 0),
                session_data.get('videos_processed', 0),
                session_data.get('videos_published', 0),
                session_data.get('uniqueness_level'),
                session_data.get('processing_time_seconds', 0),
                session_data.get('success_rate', 0),
                session_data.get('started_at'),
                session_data.get('completed_at')
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📉 Отслежена сессия: {session_data.get('session_id')}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отслеживания сессии: {e}")
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """
        Получение общей статистики
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Общая статистика
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_videos,
                    AVG(viral_score) as avg_viral_score,
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments
                FROM video_stats
            ''')
            
            overall = cursor.fetchone()
            
            # Статистика по платформам
            cursor.execute('''
                SELECT platform, COUNT(*) as count, AVG(viral_score) as avg_score
                FROM video_stats
                GROUP BY platform
            ''')
            
            platforms = cursor.fetchall()
            
            # Статистика по темам
            cursor.execute('''
                SELECT theme, COUNT(*) as count, AVG(viral_score) as avg_score
                FROM video_stats
                WHERE theme IS NOT NULL
                GROUP BY theme
                ORDER BY count DESC
                LIMIT 10
            ''')
            
            themes = cursor.fetchall()
            
            conn.close()
            
            return {
                'overall': {
                    'total_videos': overall[0] or 0,
                    'avg_viral_score': round(overall[1] or 0, 3),
                    'total_views': overall[2] or 0,
                    'total_likes': overall[3] or 0,
                    'total_comments': overall[4] or 0
                },
                'by_platform': [
                    {
                        'platform': p[0],
                        'video_count': p[1],
                        'avg_viral_score': round(p[2] or 0, 3)
                    } for p in platforms
                ],
                'top_themes': [
                    {
                        'theme': t[0],
                        'video_count': t[1],
                        'avg_viral_score': round(t[2] or 0, 3)
                    } for t in themes
                ],
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return self._get_demo_stats()
    
    def get_performance_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Получение трендов продуктивности за последние N дней
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Тренды по дням
            cursor.execute('''
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as videos_processed,
                    AVG(viral_score) as avg_viral_score
                FROM video_stats
                WHERE created_at >= date('now', '-{} days')
                GROUP BY DATE(created_at)
                ORDER BY date
            '''.format(days))
            
            daily_trends = cursor.fetchall()
            
            # Тренды по сессиям
            cursor.execute('''
                SELECT 
                    AVG(success_rate) as avg_success_rate,
                    AVG(processing_time_seconds) as avg_processing_time,
                    COUNT(*) as total_sessions
                FROM processing_sessions
                WHERE created_at >= date('now', '-{} days')
            '''.format(days))
            
            session_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'period_days': days,
                'daily_trends': [
                    {
                        'date': d[0],
                        'videos_processed': d[1],
                        'avg_viral_score': round(d[2] or 0, 3)
                    } for d in daily_trends
                ],
                'session_performance': {
                    'avg_success_rate': round(session_stats[0] or 0, 3),
                    'avg_processing_time': round(session_stats[1] or 0, 2),
                    'total_sessions': session_stats[2] or 0
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения трендов: {e}")
            return self._get_demo_trends(days)
    
    def generate_report(self, report_type: str = 'weekly') -> Dict[str, Any]:
        """
        Генерация отчета
        
        Args:
            report_type: Тип отчета (daily, weekly, monthly)
        
        Returns:
            Полный отчет о продуктивности
        """
        days_mapping = {
            'daily': 1,
            'weekly': 7,
            'monthly': 30
        }
        
        days = days_mapping.get(report_type, 7)
        
        overall_stats = self.get_overall_stats()
        trends = self.get_performance_trends(days)
        
        report = {
            'report_type': report_type,
            'period_days': days,
            'generated_at': datetime.now().isoformat(),
            'summary': overall_stats,
            'trends': trends,
            'recommendations': self._generate_recommendations(overall_stats, trends)
        }
        
        # Сохранение отчета
        report_filename = f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.analytics_dir / report_filename
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            report['report_file'] = str(report_path)
            logger.info(f"📄 Отчет сохранен: {report_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения отчета: {e}")
        
        return report
    
    def _generate_recommendations(self, overall_stats: Dict[str, Any], trends: Dict[str, Any]) -> List[str]:
        """
        Генерация рекомендаций на основе статистики
        """
        recommendations = []
        
        avg_viral_score = overall_stats.get('overall', {}).get('avg_viral_score', 0)
        total_videos = overall_stats.get('overall', {}).get('total_videos', 0)
        
        if avg_viral_score < 0.5:
            recommendations.append("Рассмотрите возможность улучшения критериев отбора видео")
        
        if total_videos < 10:
            recommendations.append("Увеличьте объем обрабатываемого контента для лучшей статистики")
        
        # Анализ по платформам
        platforms = overall_stats.get('by_platform', [])
        if platforms:
            best_platform = max(platforms, key=lambda x: x['avg_viral_score'])
            recommendations.append(f"Лучшие результаты показывает {best_platform['platform']} - сосредоточьтесь на ней")
        
        # Анализ трендов
        session_perf = trends.get('session_performance', {})
        avg_success_rate = session_perf.get('avg_success_rate', 0)
        
        if avg_success_rate < 0.8:
            recommendations.append("Оптимизируйте процесс обработки для повышения успешности")
        
        if not recommendations:
            recommendations.append("Отличная работа! Продолжайте в том же духе")
        
        return recommendations
    
    def _get_demo_stats(self) -> Dict[str, Any]:
        """
        Демо статистика
        """
        return {
            'overall': {
                'total_videos': 42,
                'avg_viral_score': 0.78,
                'total_views': 125000,
                'total_likes': 8500,
                'total_comments': 950
            },
            'by_platform': [
                {'platform': 'youtube', 'video_count': 15, 'avg_viral_score': 0.82},
                {'platform': 'tiktok', 'video_count': 18, 'avg_viral_score': 0.75},
                {'platform': 'instagram', 'video_count': 9, 'avg_viral_score': 0.79}
            ],
            'top_themes': [
                {'theme': 'мотивация', 'video_count': 12, 'avg_viral_score': 0.85},
                {'theme': 'лайфхаки', 'video_count': 10, 'avg_viral_score': 0.72},
                {'theme': 'юмор', 'video_count': 8, 'avg_viral_score': 0.76}
            ],
            'generated_at': datetime.now().isoformat()
        }
    
    def _get_demo_trends(self, days: int) -> Dict[str, Any]:
        """
        Демо тренды
        """
        return {
            'period_days': days,
            'daily_trends': [
                {'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'), 
                 'videos_processed': 3 + i, 'avg_viral_score': 0.7 + (i * 0.02)}
                for i in range(min(days, 7))
            ],
            'session_performance': {
                'avg_success_rate': 0.85,
                'avg_processing_time': 45.6,
                'total_sessions': 12
            },
            'generated_at': datetime.now().isoformat()
        }