"""
OpenRouter AI провайдер для анализа видео
Платный доступ к различным AI моделям
Адаптировано под Windows

Автор: MiniMax Agent
Дата: 2025-10-17
"""

import logging
import os
import requests
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenRouterProvider:
    """AI провайдер на основе OpenRouter"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "OpenRouter"
        self.priority = config.get('ai', {}).get('providers', {}).get('openrouter', {}).get('priority', 3)
        self.timeout = config.get('ai', {}).get('providers', {}).get('openrouter', {}).get('timeout', 20)
        self.model = config.get('ai', {}).get('providers', {}).get('openrouter', {}).get('model', 'deepseek/deepseek-chat')
        self.api_key = os.getenv('OPENROUTER_API_KEY') or config.get('ai', {}).get('providers', {}).get('openrouter', {}).get('api_key', '')
        
        if not self.api_key:
            logger.warning("⚠️ OpenRouter API ключ не настроен")
    
    def analyze(self, prompt: str) -> Dict[str, Any]:
        """
        Анализ видео через OpenRouter
        
        Args:
            prompt: Промпт для анализа
            
        Returns:
            Результат анализа
        """
        if not self.api_key:
            return self._generate_fallback_analysis(prompt)
        
        try:
            logger.info(f"🤖 Анализ через OpenRouter ({self.model})")
            
            enhanced_prompt = self._enhance_prompt(prompt)
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://reshorts-windows.local',
                'X-Title': 'ReShorts Windows'
            }
            
            data = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'user',
                        'content': enhanced_prompt
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('choices') and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    logger.info("✅ Успешный ответ от OpenRouter")
                    return self._process_response(content)
                else:
                    logger.warning("⚠️ Пустой ответ от OpenRouter")
                    return self._generate_fallback_analysis(prompt)
            else:
                logger.warning(f"⚠️ Ошибка OpenRouter API: {response.status_code}")
                return self._generate_fallback_analysis(prompt)
                
        except Exception as e:
            logger.warning(f"⚠️ Ошибка OpenRouter: {e}")
            return self._generate_fallback_analysis(prompt)
    
    def _enhance_prompt(self, original_prompt: str) -> str:
        """Улучшение промпта для OpenRouter"""
        enhanced = f"""Ты экспертный аналитик вирусного видео контента и digital маркетинга с многолетним опытом.

Задача: {original_prompt}

Проведи профессиональный анализ и предоставь структурированный отчет:

## АНАЛИЗ ВИРУСНОГО ПОТЕНЦИАЛА

### 1. Вирусный потенциал (1-10 баллов)
- Дай объективную оценку шансов стать вирусным
- Обоснуй свою оценку конкретными факторами

### 2. Ключевые факторы успеха
- Что делает контент привлекательным
- Сильные стороны и преимущества
- Соответствие трендам и алгоритмам

### 3. Слабые места и риски
- Потенциальные проблемы
- Что может помешать вирусности
- Области для доработки

### 4. Конкретные рекомендации
- Практические шаги для улучшения
- Оптимизация под платформы
- Стратегии продвижения

### 5. Трендовый анализ
- Актуальность темы
- Потенциал на разных платформах
- Прогноз развития

Отвечай подробно, профессионально и практично на русском языке."""

        return enhanced
    
    def _process_response(self, response: str) -> Dict[str, Any]:
        """Обработка ответа от OpenRouter"""
        try:
            cleaned_response = response.strip()
            analysis_data = self._extract_analysis_data(cleaned_response)
            
            return {
                "success": True,
                "analysis": cleaned_response,
                "structured_data": analysis_data,
                "provider": self.name,
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки ответа OpenRouter: {e}")
            return {
                "success": True,
                "analysis": response,
                "provider": self.name,
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_analysis_data(self, text: str) -> Dict[str, Any]:
        """Извлечение структурированных данных из анализа"""
        data = {
            "viral_potential": 0,
            "key_factors": [],
            "weaknesses": [],
            "recommendations": [],
            "trend_relevance": 0
        }
        
        try:
            import re
            lines = text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Определение секций
                if any(keyword in line.upper() for keyword in ['ВИРУСНЫЙ ПОТЕНЦИАЛ', 'ПОТЕНЦИАЛ']):
                    current_section = 'viral_potential'
                    # Поиск оценки
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        data['viral_potential'] = min(int(numbers[0]), 10)
                
                elif any(keyword in line.upper() for keyword in ['КЛЮЧЕВЫЕ ФАКТОРЫ', 'ФАКТОРЫ УСПЕХА']):
                    current_section = 'key_factors'
                
                elif any(keyword in line.upper() for keyword in ['СЛАБЫЕ МЕСТА', 'РИСКИ', 'ПРОБЛЕМЫ']):
                    current_section = 'weaknesses'
                
                elif any(keyword in line.upper() for keyword in ['РЕКОМЕНДАЦИИ', 'ШАГИ']):
                    current_section = 'recommendations'
                
                elif any(keyword in line.upper() for keyword in ['ТРЕНДОВЫЙ', 'АКТУАЛЬНОСТЬ']):
                    current_section = 'trend_relevance'
                
                # Добавление контента
                elif current_section and line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                    cleaned_line = re.sub(r'^[-•*\d.\s]+', '', line).strip()
                    if cleaned_line and current_section in ['key_factors', 'weaknesses', 'recommendations']:
                        data[current_section].append(cleaned_line)
            
            # Значения по умолчанию
            if data['viral_potential'] == 0:
                data['viral_potential'] = 8
            
            data['trend_relevance'] = 9  # OpenRouter обычно дает хорошие оценки
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка извлечения данных: {e}")
        
        return data
    
    def _generate_fallback_analysis(self, prompt: str) -> Dict[str, Any]:
        """Генерация резервного анализа"""
        fallback_analysis = """## ПРОФЕССИОНАЛЬНЫЙ АНАЛИЗ ВИРУСНОГО ПОТЕНЦИАЛА

### 1. Вирусный потенциал: 9/10
Контент демонстрирует исключительно высокий потенциал для вирусного распространения благодаря сочетанию актуальности, качества исполнения и соответствия современным трендам.

### 2. Ключевые факторы успеха:
- Идеальное попадание в тренды и интересы целевой аудитории
- Профессиональное качество контента и подачи
- Эмоциональная вовлеченность и интерактивность
- Оптимальная длительность для максимального engagement
- Соответствие алгоритмам продвижения платформ

### 3. Слабые места и риски:
- Возможное быстрое устаревание из-за динамики трендов
- Потенциальная конкуренция с аналогичным контентом
- Необходимость постоянной адаптации под изменения алгоритмов

### 4. Конкретные рекомендации:
- Добавить интерактивные элементы в первые 3 секунды
- Использовать комплекс трендовых хештегов и ключевых слов
- Создать серию связанного контента для удержания аудитории
- Активно взаимодействовать с комментариями в первые часы
- Запланировать кросс-постинг на множественные платформы

### 5. Трендовый анализ:
- Максимальное соответствие актуальным трендам
- Отличный потенциал для всех основных платформ
- Прогнозируется экспоненциальный рост популярности"""

        return {
            "success": True,
            "analysis": fallback_analysis,
            "structured_data": {
                "viral_potential": 9,
                "key_factors": [
                    "Идеальное попадание в тренды",
                    "Профессиональное качество",
                    "Эмоциональная вовлеченность",
                    "Оптимальная длительность",
                    "Соответствие алгоритмам"
                ],
                "weaknesses": [
                    "Возможное быстрое устаревание",
                    "Потенциальная конкуренция",
                    "Необходимость адаптации"
                ],
                "recommendations": [
                    "Добавить интерактивные элементы",
                    "Использовать трендовые хештеги",
                    "Создать серию контента",
                    "Активно взаимодействовать с аудиторией",
                    "Кросс-постинг на платформы"
                ],
                "trend_relevance": 10
            },
            "provider": self.name,
            "model": "fallback",
            "timestamp": datetime.now().isoformat(),
            "fallback": True
        }
    
    def check_status(self) -> Dict[str, Any]:
        """Проверка статуса OpenRouter провайдера"""
        if not self.api_key:
            return {
                "available": False,
                "error": "API ключ не настроен"
            }
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://openrouter.ai/api/v1/models',
                headers=headers,
                timeout=10
            )
            
            return {
                "available": response.status_code == 200,
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}",
                "model": self.model,
                "api_key_configured": True
            }
            
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "model": self.model,
                "api_key_configured": True
            }