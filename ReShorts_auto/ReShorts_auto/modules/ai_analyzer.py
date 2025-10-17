#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Analyzer - Модуль AI анализа вирусного потенциала
Локальные AI модели для анализа контента
"""

import re
import math
from datetime import datetime, timedelta
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from loguru import logger
import json
from pathlib import Path
import cv2
import random
from langdetect import detect, LangDetectError

class AIAnalyzer:
    """Класс для AI анализа вирусного потенциала"""
    
    def __init__(self, config):
        self.config = config
        self.viral_threshold = config.get('ai_analysis', {}).get('viral_threshold', 0.7)
        self.analyze_emotions = config.get('ai_analysis', {}).get('analyze_emotions', True)
        
        # Ключевые слова для вирусного контента
        self.viral_keywords = {
            'ru': [
                'вирусно', 'тренд', 'хайп', 'бомба', 'огонь',
                'шок', 'невероятно', 'удивительно', 'смешно', 'круто',
                'вау', 'омг', 'лол', 'мем', 'взрыв', 'топ', 'лучшие'
            ],
            'en': [
                'viral', 'trending', 'amazing', 'incredible', 'shocking', 'unbelievable',
                'wow', 'omg', 'lol', 'epic', 'best', 'top', 'fire', 'crazy', 'insane',
                'mindblowing', 'hilarious', 'awesome', 'fantastic', 'legendary'
            ]
        }
        
        # Эмоциональные маркеры
        self.emotion_keywords = {
            'positive': {
                'ru': ['счастлив', 'радост', 'весел', 'позитив', 'люблю', 'обожаю'],
                'en': ['happy', 'joy', 'love', 'amazing', 'wonderful', 'fantastic', 'great']
            },
            'negative': {
                'ru': ['грустн', 'страшн', 'плох', 'ужасн', 'зл', 'расстроен'],
                'en': ['sad', 'angry', 'terrible', 'awful', 'bad', 'hate', 'disgusting']
            },
            'surprise': {
                'ru': ['удивлен', 'шок', 'неожиданн', 'вау', 'омг'],
                'en': ['surprised', 'shocked', 'wow', 'omg', 'unbelievable', 'incredible']
            }
        }
        
        # Трендовые хештеги и темы
        self.trending_topics = [
            '#fyp', '#viral', '#trending', '#foryou', '#foryoupage',
            '#тренд', '#вирусно', '#рекомендации',
            '#challenge', '#dance', '#comedy', '#music', '#lifestyle'
        ]
    
    def analyze_viral_potential(self, video_info):
        """Основной метод анализа вирусного потенциала"""
        logger.info(f"Начало AI анализа: {video_info.get('title', 'Unknown')[:50]}...")
        
        try:
            analysis_result = {
                'viral_score': 0.0,
                'confidence': 0.0,
                'factors': {},
                'recommendations': [],
                'emotions': {},
                'trending_score': 0.0,
                'engagement_prediction': {},
                'optimal_posting_time': self._suggest_posting_time(),
                'target_audience': self._analyze_target_audience(video_info),
                'content_type': self._classify_content_type(video_info),
                'risk_assessment': self._assess_content_risks(video_info)
            }
            
            # Анализ метрик вовлеченности
            engagement_score = self._analyze_engagement_metrics(video_info)
            analysis_result['factors']['engagement'] = engagement_score
            
            # Анализ текстового контента
            text_score = self._analyze_text_content(video_info)
            analysis_result['factors']['text_content'] = text_score
            
            # Анализ тайминга
            timing_score = self._analyze_timing(video_info)
            analysis_result['factors']['timing'] = timing_score
            
            # Анализ трендов
            trending_score = self._analyze_trending_factors(video_info)
            analysis_result['factors']['trending'] = trending_score
            analysis_result['trending_score'] = trending_score
            
            # Анализ платформы
            platform_score = self._analyze_platform_factors(video_info)
            analysis_result['factors']['platform'] = platform_score
            
            # Анализ эмоций
            if self.analyze_emotions:
                emotions = self._analyze_emotions(video_info)
                analysis_result['emotions'] = emotions
                analysis_result['factors']['emotions'] = emotions.get('overall_score', 0.5)
            
            # Вычисление общего скора
            viral_score = self._calculate_overall_score(analysis_result['factors'])
            analysis_result['viral_score'] = viral_score
            
            # Оценка уверенности
            confidence = self._calculate_confidence(analysis_result['factors'])
            analysis_result['confidence'] = confidence
            
            # Прогноз вовлеченности
            engagement_prediction = self._predict_engagement(video_info, viral_score)
            analysis_result['engagement_prediction'] = engagement_prediction
            
            # Генерация рекомендаций
            recommendations = self._generate_recommendations(analysis_result)
            analysis_result['recommendations'] = recommendations
            
            logger.info(f"Анализ завершен. Вирусный скор: {viral_score:.2f}/10")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Ошибка AI анализа: {e}")
            return self._get_default_analysis()
    
    def _analyze_engagement_metrics(self, video_info):
        """Анализ метрик вовлеченности"""
        views = video_info.get('views', 0)
        likes = video_info.get('likes', 0)
        comments = video_info.get('comments', 0)
        shares = video_info.get('shares', 0)
        
        if views == 0:
            return 0.1
        
        # Отношения вовлеченности
        like_ratio = likes / views
        comment_ratio = comments / views
        share_ratio = shares / views
        
        # Нормализация метрик
        like_score = min(like_ratio * 100, 1.0)  # Отлично, если > 1% лайков
        comment_score = min(comment_ratio * 1000, 1.0)  # Отлично, если > 0.1% комментариев
        share_score = min(share_ratio * 500, 1.0)  # Отлично, если > 0.2% репостов
        
        # Общий скор вовлеченности
        engagement_score = (like_score * 0.4 + comment_score * 0.3 + share_score * 0.3)
        
        # Бонус за высокое количество просмотров
        if views > 1000000:  # 1M+
            engagement_score *= 1.2
        elif views > 100000:  # 100K+
            engagement_score *= 1.1
        
        return min(engagement_score, 1.0)
    
    def _analyze_text_content(self, video_info):
        """Анализ текстового контента (заголовок, описание)"""
        title = video_info.get('title', '').lower()
        description = video_info.get('description', '').lower()
        author = video_info.get('author', '').lower()
        
        text_content = f"{title} {description} {author}"
        
        if not text_content.strip():
            return 0.3  # Нетральная оценка без текста
        
        score = 0.0
        
        # Определяем язык
        try:
            language = detect(text_content)
        except LangDetectError:
            language = 'en'
        
        # Поиск вирусных ключевых слов
        viral_words = self.viral_keywords.get(language, self.viral_keywords['en'])
        viral_count = sum(1 for word in viral_words if word in text_content)
        
        if viral_count > 0:
            score += min(viral_count * 0.2, 0.6)  # Макс 0.6 за вирусные слова
        
        # Поиск трендовых хештегов
        hashtag_count = sum(1 for tag in self.trending_topics if tag in text_content)
        if hashtag_count > 0:
            score += min(hashtag_count * 0.1, 0.3)
        
        # Оценка длины заголовка (оптимально 10-60 символов)
        title_len = len(title)
        if 10 <= title_len <= 60:
            score += 0.1
        elif title_len > 60:
            score -= 0.05  # Пенальти за слишком длинный заголовок
        
        # Поиск вопросов и восклицаний (повышает вовлеченность)
        if '?' in title or '!' in title:
            score += 0.1
        
        # Поиск чисел в заголовке (часто привлекает внимание)
        if re.search(r'\d', title):
            score += 0.05
        
        # Поиск эмодзи (может повышать вовлеченность)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # эмотиконы
            "\U0001F300-\U0001F5FF"  # символы и пиктограммы
            "\U0001F680-\U0001F6FF"  # транспорт и карты
            "\U0001F1E0-\U0001F1FF"  # флаги
            "]+", flags=re.UNICODE)
        
        if emoji_pattern.search(text_content):
            score += 0.05
        
        return min(score, 1.0)
    
    def _analyze_timing(self, video_info):
        """Анализ временных факторов"""
        duration = video_info.get('duration', 0)
        
        # Оптимальная длительность для shorts: 15-60 секунд
        if 15 <= duration <= 60:
            duration_score = 1.0
        elif 10 <= duration < 15 or 60 < duration <= 90:
            duration_score = 0.8
        elif duration < 10:
            duration_score = 0.5  # Слишком коротко
        else:
            duration_score = 0.3  # Слишком длинно
        
        # Анализ времени публикации (если доступно)
        upload_time_score = 0.5  # Нейтрально по умолчанию
        
        created_at = video_info.get('created_at')
        if created_at:
            try:
                upload_datetime = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                hour = upload_datetime.hour
                
                # Оптимальное время для публикации: 18-22 часа и 9-12
                if 18 <= hour <= 22 or 9 <= hour <= 12:
                    upload_time_score = 1.0
                elif 15 <= hour < 18 or 12 < hour < 15:
                    upload_time_score = 0.8
                else:
                    upload_time_score = 0.4
                    
            except Exception:
                pass
        
        return (duration_score * 0.7 + upload_time_score * 0.3)
    
    def _analyze_trending_factors(self, video_info):
        """Анализ трендовых факторов"""
        title = video_info.get('title', '').lower()
        description = video_info.get('description', '').lower()
        
        text_content = f"{title} {description}"
        score = 0.0
        
        # Поиск трендовых хештегов
        trending_count = sum(1 for tag in self.trending_topics if tag in text_content)
        score += min(trending_count * 0.2, 0.6)
        
        # Поиск слов связанных с челленджами
        challenge_words = ['challenge', 'челлендж', 'trend', 'тренд', 'viral', 'вирусно']
        challenge_count = sum(1 for word in challenge_words if word in text_content)
        score += min(challenge_count * 0.15, 0.3)
        
        # Оценка новизны (молодые тренды чаще становятся вирусными)
        created_at = video_info.get('created_at')
        if created_at:
            try:
                upload_datetime = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (datetime.now() - upload_datetime).days
                
                if days_old <= 1:
                    score += 0.2  # Очень свежее
                elif days_old <= 7:
                    score += 0.1  # Новое
                elif days_old > 30:
                    score -= 0.1  # Старое
                    
            except Exception:
                pass
        
        return min(score, 1.0)
    
    def _analyze_platform_factors(self, video_info):
        """Анализ факторов платформы"""
        platform = video_info.get('platform', '').lower()
        author = video_info.get('author', '').lower()
        
        score = 0.5  # Базовая оценка
        
        # Оценка платформы
        if platform == 'tiktok':
            score += 0.3  # TikTok оптимален для вирусного контента
        elif platform == 'youtube':
            score += 0.2  # YouTube Shorts тоже хорошо
        elif platform == 'instagram':
            score += 0.15  # Instagram Reels
        
        # Оценка популярности автора
        # (в реальном проекте можно получать статистику автора)
        views = video_info.get('views', 0)
        if views > 500000:
            score += 0.1  # Популярный автор
        
        return min(score, 1.0)
    
    def _analyze_emotions(self, video_info):
        """Анализ эмоциональной окраски контента"""
        title = video_info.get('title', '').lower()
        description = video_info.get('description', '').lower()
        text_content = f"{title} {description}"
        
        emotions = {
            'positive': 0.0,
            'negative': 0.0,
            'surprise': 0.0,
            'overall_score': 0.5,
            'dominant_emotion': 'neutral'
        }
        
        if not text_content.strip():
            return emotions
        
        # Определяем язык
        try:
            language = detect(text_content)
        except LangDetectError:
            language = 'en'
        
        # Подсчитываем эмоциональные маркеры
        for emotion_type, keywords_dict in self.emotion_keywords.items():
            keywords = keywords_dict.get(language, keywords_dict.get('en', []))
            count = sum(1 for keyword in keywords if keyword in text_content)
            emotions[emotion_type] = min(count * 0.3, 1.0)
        
        # TextBlob анализ (только для английского)
        if language == 'en':
            try:
                blob = TextBlob(text_content)
                polarity = blob.sentiment.polarity  # -1 до 1
                
                if polarity > 0.3:
                    emotions['positive'] = max(emotions['positive'], polarity)
                elif polarity < -0.3:
                    emotions['negative'] = max(emotions['negative'], abs(polarity))
                    
            except Exception:
                pass
        
        # Определяем доминирующую эмоцию
        max_emotion = max(emotions['positive'], emotions['negative'], emotions['surprise'])
        
        if emotions['positive'] == max_emotion and max_emotion > 0.3:
            emotions['dominant_emotion'] = 'positive'
            emotions['overall_score'] = 0.7 + emotions['positive'] * 0.3
        elif emotions['surprise'] == max_emotion and max_emotion > 0.3:
            emotions['dominant_emotion'] = 'surprise'
            emotions['overall_score'] = 0.8 + emotions['surprise'] * 0.2  # Удивление часто вирусно
        elif emotions['negative'] == max_emotion and max_emotion > 0.3:
            emotions['dominant_emotion'] = 'negative'
            emotions['overall_score'] = 0.3 + emotions['negative'] * 0.2  # Негатив меньше вирусен
        
        return emotions
    
    def _calculate_overall_score(self, factors):
        """Вычисление общего вирусного скора"""
        weights = {
            'engagement': 0.35,
            'text_content': 0.25,
            'trending': 0.20,
            'timing': 0.10,
            'platform': 0.05,
            'emotions': 0.05
        }
        
        total_score = 0.0
        for factor, weight in weights.items():
            factor_score = factors.get(factor, 0.5)
            total_score += factor_score * weight
        
        # Нормализация до 10-балльной шкалы
        viral_score = total_score * 10
        
        return round(min(viral_score, 10.0), 1)
    
    def _calculate_confidence(self, factors):
        """Вычисление уровня уверенности в оценке"""
        # Уверенность зависит от количества доступных данных
        available_factors = len([f for f in factors.values() if f > 0])
        max_factors = len(factors)
        
        base_confidence = available_factors / max_factors
        
        # Бонус за качество данных
        engagement_factor = factors.get('engagement', 0)
        if engagement_factor > 0.8:
            base_confidence += 0.1
        
        return round(min(base_confidence, 1.0), 2)
    
    def _predict_engagement(self, video_info, viral_score):
        """Прогноз вовлеченности"""
        current_views = video_info.get('views', 0)
        
        # Прогноз на основе вирусного скора
        growth_multiplier = 1 + (viral_score / 10) * 2  # От 1 до 3
        
        predicted_views = int(current_views * growth_multiplier)
        predicted_likes = int(predicted_views * 0.03)  # 3% от просмотров
        predicted_comments = int(predicted_views * 0.005)  # 0.5%
        predicted_shares = int(predicted_views * 0.01)  # 1%
        
        return {
            'predicted_views': predicted_views,
            'predicted_likes': predicted_likes,
            'predicted_comments': predicted_comments,
            'predicted_shares': predicted_shares,
            'growth_potential': f"{int((growth_multiplier - 1) * 100)}%",
            'time_to_peak': self._estimate_peak_time(viral_score)
        }
    
    def _estimate_peak_time(self, viral_score):
        """Оценка времени до пика популярности"""
        if viral_score >= 8.0:
            return "Менее 24 часов"
        elif viral_score >= 6.0:
            return "1-3 дня"
        elif viral_score >= 4.0:
            return "3-7 дней"
        else:
            return "Медленный рост"
    
    def _suggest_posting_time(self):
        """Предложение оптимального времени публикации"""
        # Оптимальные часы для публикации
        optimal_hours = {
            'утро': [9, 10, 11],
            'день': [14, 15, 16],
            'вечер': [18, 19, 20, 21]
        }
        
        current_hour = datetime.now().hour
        
        for period, hours in optimal_hours.items():
            if current_hour in hours:
                return f"Сейчас ({period})"
        
        # Найти следующее оптимальное время
        all_optimal = [h for hours in optimal_hours.values() for h in hours]
        next_optimal = min([h for h in all_optimal if h > current_hour], default=all_optimal[0])
        
        if next_optimal < current_hour:
            return f"Завтра в {next_optimal}:00"
        else:
            return f"Сегодня в {next_optimal}:00"
    
    def _analyze_target_audience(self, video_info):
        """Анализ целевой аудитории"""
        title = video_info.get('title', '').lower()
        platform = video_info.get('platform', '').lower()
        
        # Простой анализ на основе ключевых слов
        if any(word in title for word in ['гейм', 'game', 'игра']):
            return "Геймеры (13-25 лет)"
        elif any(word in title for word in ['музык', 'music', 'песн']):
            return "Музыкальная аудитория (16-30 лет)"
        elif any(word in title for word in ['комеди', 'funny', 'смеш']):
            return "Любители юмора (18-35 лет)"
        elif platform == 'tiktok':
            return "Gen Z (16-25 лет)"
        else:
            return "Широкая аудитория (16-35 лет)"
    
    def _classify_content_type(self, video_info):
        """Классификация типа контента"""
        title = video_info.get('title', '').lower()
        
        content_types = {
            'Обучающий': ['как', 'how', 'учим', 'learn', 'лайфхак'],
            'Развлекательный': ['смеш', 'funny', 'прикол', 'юмор'],
            'Музыкальный': ['музык', 'music', 'песн', 'song', 'танец'],
            'Лайфстайл': ['лайфстайл', 'lifestyle', 'жизнь', 'день'],
            'Бьюти': ['макияж', 'makeup', 'красота', 'beauty'],
            'Спорт': ['спорт', 'sport', 'тренировка', 'workout']
        }
        
        for content_type, keywords in content_types.items():
            if any(keyword in title for keyword in keywords):
                return content_type
        
        return 'Общий'
    
    def _assess_content_risks(self, video_info):
        """Оценка рисков контента"""
        title = video_info.get('title', '').lower()
        description = video_info.get('description', '').lower()
        text_content = f"{title} {description}"
        
        risks = {
            'copyright_risk': 'low',
            'content_policy_risk': 'low',
            'overall_risk': 'low'
        }
        
        # Проверка авторских прав
        copyright_words = ['official', 'официальн', 'original', 'клип']
        if any(word in text_content for word in copyright_words):
            risks['copyright_risk'] = 'medium'
        
        # Проверка на потенциально проблемный контент
        sensitive_words = ['конфликт', 'политик', 'скандал']
        if any(word in text_content for word in sensitive_words):
            risks['content_policy_risk'] = 'medium'
        
        # Общая оценка риска
        if risks['copyright_risk'] == 'medium' or risks['content_policy_risk'] == 'medium':
            risks['overall_risk'] = 'medium'
        
        return risks
    
    def _generate_recommendations(self, analysis_result):
        """Генерация рекомендаций по улучшению"""
        recommendations = []
        viral_score = analysis_result['viral_score']
        factors = analysis_result['factors']
        
        # Рекомендации на основе скора
        if viral_score >= 8.0:
            recommendations.append("🔥 Отличный вирусный потенциал! Публикуйте немедленно")
        elif viral_score >= 6.0:
            recommendations.append("✨ Хороший потенциал. Можно публиковать")
        elif viral_score >= 4.0:
            recommendations.append("📈 Средний потенциал. Рассмотрите улучшения")
        else:
            recommendations.append("⚠️ Низкий потенциал. Нужны существенные улучшения")
        
        # Специфичные рекомендации
        if factors.get('engagement', 0) < 0.5:
            recommendations.append("📈 Улучшите вовлеченность: добавьте CTA, вопросы к аудитории")
        
        if factors.get('text_content', 0) < 0.5:
            recommendations.append("✏️ Улучшите заголовок: добавьте эмоции, вирусные слова")
        
        if factors.get('trending', 0) < 0.5:
            recommendations.append("🔥 Добавьте трендовые хештеги и слова")
        
        if factors.get('timing', 0) < 0.5:
            recommendations.append("⏰ Оптимизируйте длительность (15-60 сек) и время публикации")
        
        # Общие рекомендации
        recommendations.extend([
            "🎥 Добавьте яркие визуальные эффекты",
            "📱 Оптимизируйте для мобильного просмотра",
            "🔊 Используйте трендовую музыку"
        ])
        
        return recommendations[:5]  # Максимум 5 рекомендаций
    
    def _get_default_analysis(self):
        """Анализ по умолчанию при ошибке"""
        return {
            'viral_score': 5.0,
            'confidence': 0.3,
            'factors': {
                'engagement': 0.5,
                'text_content': 0.5,
                'timing': 0.5,
                'trending': 0.5,
                'platform': 0.5,
                'emotions': 0.5
            },
            'recommendations': [
                "⚠️ Ограниченные данные для анализа",
                "📈 Добавьте больше метаданных для лучшего анализа"
            ],
            'emotions': {
                'positive': 0.5,
                'negative': 0.2,
                'surprise': 0.3,
                'overall_score': 0.5,
                'dominant_emotion': 'neutral'
            },
            'trending_score': 0.5,
            'engagement_prediction': {
                'predicted_views': 0,
                'predicted_likes': 0,
                'predicted_comments': 0,
                'predicted_shares': 0,
                'growth_potential': '0%',
                'time_to_peak': 'Неопределено'
            },
            'optimal_posting_time': self._suggest_posting_time(),
            'target_audience': 'Общая аудитория',
            'content_type': 'Общий',
            'risk_assessment': {
                'copyright_risk': 'low',
                'content_policy_risk': 'low',
                'overall_risk': 'low'
            }
        }