#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для AI анализа контента и определения вирусного потенциала

Автор: MiniMax Agent
Дата: 2025-10-17
"""

import openai
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """
    Класс для AI анализа видеоконтента
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        api_key = config.get('api_keys', {}).get('openai_api_key')
        if api_key:
            openai.api_key = api_key
            self.ai_available = True
        else:
            self.ai_available = False
            logger.warning("OpenAI API ключ не найден, AI анализ недоступен")
    
    def analyze_viral_potential(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Анализ вирусного потенциала видео
        
        Args:
            videos: Список видео для анализа
        
        Returns:
            Список видео с добавленными AI метриками
        """
        logger.info(f"🧠 AI анализ {len(videos)} видео")
        
        analyzed_videos = []
        for video in videos:
            analysis = self._analyze_single_video(video)
            video.update(analysis)
            analyzed_videos.append(video)
        
        # Сортировка по AI потенциалу
        analyzed_videos.sort(key=lambda x: x.get('ai_potential', 0), reverse=True)
        
        return analyzed_videos
    
    def _analyze_single_video(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализ одного видео
        """
        if not self.ai_available:
            return self._generate_demo_analysis(video)
        
        try:
            # Подготовка данных для анализа
            analysis_prompt = self._create_analysis_prompt(video)
            
            # Запрос к OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты эксперт по анализу вирусного контента в социальных сетях."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response)
            
        except Exception as e:
            logger.error(f"❌ Ошибка AI анализа: {e}")
            return self._generate_demo_analysis(video)
    
    def _create_analysis_prompt(self, video: Dict[str, Any]) -> str:
        """
        Создание промпта для AI анализа
        """
        return f"""
Проанализируй вирусный потенциал этого видео:

Название: {video.get('title', '')}
Описание: {video.get('description', '')[:200]}...
Платформа: {video.get('platform', '')}
Просмотры: {video.get('views', 0):,}
Лайки: {video.get('likes', 0):,}
Комментарии: {video.get('comments', 0):,}
Текущий вирусный счет: {video.get('viral_score', 0)}

Оцени по шкале от 0 до 1:
1. AI потенциал (общая оценка)
2. Качество контента
3. Уровень вовлеченности
4. Потенциал для уникализации
5. Рекомендация к использованию

Ответ должен быть в формате JSON:
{{
  "ai_potential": 0.85,
  "content_quality": 0.9,
  "engagement_level": 0.8,
  "uniqueness_potential": 0.75,
  "recommendation": "high",
  "analysis_notes": "Краткий анализ"
}}
"""
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        Парсинг ответа от AI
        """
        try:
            # Извлечение JSON из ответа
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Ошибка парсинга AI ответа: {e}")
        
        # Возвращаем значения по умолчанию при ошибке
        return self._generate_demo_analysis({})
    
    def _generate_demo_analysis(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерация демо анализа
        """
        import random
        
        return {
            'ai_potential': round(random.uniform(0.6, 0.95), 2),
            'content_quality': round(random.uniform(0.7, 0.9), 2),
            'engagement_level': round(random.uniform(0.5, 0.85), 2),
            'uniqueness_potential': round(random.uniform(0.6, 0.9), 2),
            'recommendation': random.choice(['high', 'medium', 'low']),
            'analysis_notes': "Демо анализ - AI анализ будет доступен после настройки OpenAI API",
            'analyzed_at': datetime.now().isoformat()
        }
    
    def generate_content_ideas(self, theme: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Генерация идей для контента на основе темы
        """
        logger.info(f"💡 Генерация {count} идей для темы: {theme}")
        
        if not self.ai_available:
            return self._generate_demo_ideas(theme, count)
        
        try:
            prompt = f"""
Сгенерируй {count} креативных идей для коротких видео на тему "{theme}".
Каждая идея должна быть вирусной и подходящей для YouTube Shorts, TikTok или Instagram Reels.

Формат ответа JSON:
[
  {{
    "title": "Название идеи",
    "description": "Описание концепции",
    "hook": "Цепляющий крючок для зрителя",
    "estimated_viral_potential": 0.8,
    "suggested_platform": "tiktok"
  }}
]
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты креативный директор, специализирующийся на вирусном контенте."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            return self._parse_ideas_response(ai_response)
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации идей: {e}")
            return self._generate_demo_ideas(theme, count)
    
    def _parse_ideas_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Парсинг ответа с идеями от AI
        """
        try:
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Ошибка парсинга идей: {e}")
        
        return self._generate_demo_ideas("общая тема", 3)
    
    def _generate_demo_ideas(self, theme: str, count: int) -> List[Dict[str, Any]]:
        """
        Генерация демо идей
        """
        ideas = []
        for i in range(count):
            idea = {
                'title': f"Идея {i+1} для {theme}",
                'description': f"Креативная концепция видео на тему {theme}, демо версия {i+1}",
                'hook': f"Привлекающий крючок {i+1} для темы {theme}",
                'estimated_viral_potential': round(0.6 + (i * 0.1), 1),
                'suggested_platform': ['youtube', 'tiktok', 'instagram'][i % 3],
                'generated_at': datetime.now().isoformat()
            }
            ideas.append(idea)
        
        return ideas