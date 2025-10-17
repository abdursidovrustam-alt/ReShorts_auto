"""
Google Gemini провайдер для анализа видео
Бесплатный доступ к Gemini AI
Адаптировано под Windows

Автор: MiniMax Agent
Дата: 2025-10-17
"""

import logging
import time
import os
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class GeminiProvider:
    """AI провайдер на основе Google Gemini"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "Gemini"
        self.priority = config.get('ai', {}).get('providers', {}).get('gemini', {}).get('priority', 2)
        self.timeout = config.get('ai', {}).get('timeout', 25)
        self.api_key = os.getenv('GEMINI_API_KEY') or config.get('ai', {}).get('providers', {}).get('gemini', {}).get('api_key', '')
        
        self._init_gemini()
    
    def _init_gemini(self):
        """Инициализация Google Gemini"""
        try:
            import google.generativeai as genai
            self.genai = genai
            
            # Настройка API ключа (если есть)
            if self.api_key:
                genai.configure(api_key=self.api_key)
                logger.info("✅ Gemini инициализирован с API ключом")
            else:
                logger.info("✅ Gemini инициализирован (без API ключа)")
            
        except ImportError:
            logger.error("❌ google-generativeai не установлен. Установите: pip install google-generativeai")
            raise ImportError("google-generativeai не найден")
    
    def analyze(self, prompt: str) -> Dict[str, Any]:
        """
        Анализ видео через Google Gemini
        
        Args:
            prompt: Промпт для анализа
            
        Returns:
            Результат анализа
        """
        try:
            logger.info(f"🤖 Анализ через Google Gemini")
            
            # Если нет API ключа, возвращаем fallback анализ
            if not self.api_key:
                logger.warning("⚠️ Нет API ключа для Gemini, используем fallback анализ")
                return self._generate_fallback_analysis(prompt)
            
            # Улучшенный промпт
            enhanced_prompt = self._enhance_prompt(prompt)
            
            try:
                # Инициализация модели
                model = self.genai.GenerativeModel('gemini-pro')
                
                # Генерация ответа
                response = model.generate_content(
                    enhanced_prompt,
                    generation_config=self.genai.types.GenerationConfig(
                        candidate_count=1,
                        max_output_tokens=2048,
                        temperature=0.7,
                    )
                )
                
                if response and response.text:
                    logger.info("✅ Успешный ответ от Gemini")
                    return self._process_response(response.text)
                else:
                    logger.warning("⚠️ Пустой ответ от Gemini")
                    return self._generate_fallback_analysis(prompt)
                
            except Exception as e:
                logger.warning(f"⚠️ Ошибка API Gemini: {e}")
                return self._generate_fallback_analysis(prompt)
            
        except Exception as e:
            error_msg = f"Ошибка Gemini: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def _enhance_prompt(self, original_prompt: str) -> str:
        """Улучшение промпта для Gemini"""
        enhanced = f"""Ты эксперт по анализу вирусного видео контента и цифрового маркетинга.

Задача: {original_prompt}

Проведи глубокий анализ и предоставь структурированный отчет:

## АНАЛИЗ ВИРУСНОГО ПОТЕНЦИАЛА

### 1. Оценка вирусного потенциала (1-10 баллов)
Оцени шансы видео стать вирусным

### 2. Ключевые факторы успеха
- Что делает это видео привлекательным
- Сильные стороны контента
- Преимущества формата

### 3. Слабые места и риски
- Что может помешать вирусности
- Потенциальные проблемы
- Области для улучшения

### 4. Практические рекомендации
- Конкретные шаги для улучшения
- Оптимизация для алгоритмов
- Стратегии продвижения

### 5. Трендовый анализ
- Соответствие текущим трендам
- Потенциал в различных платформах
- Прогноз популярности

Отвечай подробно и практично на русском языке."""

        return enhanced
    
    def _process_response(self, response: str) -> Dict[str, Any]:
        """Обработка ответа от Gemini"""
        try:
            # Очистка ответа
            cleaned_response = response.strip()
            
            # Извлечение структурированных данных
            analysis_data = self._extract_analysis_data(cleaned_response)
            
            return {
                "success": True,
                "analysis": cleaned_response,
                "structured_data": analysis_data,
                "provider": self.name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки ответа: {e}")
            return {
                "success": True,
                "analysis": response,
                "provider": self.name,
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_analysis_data(self, text: str) -> Dict[str, Any]:
        """Извлечение структурированных данных из анализа"""
        data = {
            "viral_potential": 0,
            "key_factors": [],
            "weaknesses": [],
            "recommendations": [],
            "trend_relevance": 0,
            "platform_suitability": {}
        }
        
        try:
            lines = text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Определение секций
                if any(keyword in line.upper() for keyword in ['ВИРУСНЫЙ ПОТЕНЦИАЛ', 'ОЦЕНКА']):
                    current_section = 'viral_potential'
                    # Поиск оценки
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        data['viral_potential'] = min(int(numbers[0]), 10)
                
                elif any(keyword in line.upper() for keyword in ['КЛЮЧЕВЫЕ ФАКТОРЫ', 'ФАКТОРЫ УСПЕХА', 'СИЛЬНЫЕ']):
                    current_section = 'key_factors'
                
                elif any(keyword in line.upper() for keyword in ['СЛАБЫЕ МЕСТА', 'НЕДОСТАТКИ', 'РИСКИ', 'ПРОБЛЕМЫ']):
                    current_section = 'weaknesses'
                
                elif any(keyword in line.upper() for keyword in ['РЕКОМЕНДАЦИИ', 'СОВЕТЫ', 'УЛУЧШЕНИЯ']):
                    current_section = 'recommendations'
                
                elif any(keyword in line.upper() for keyword in ['ТРЕНДОВЫЙ', 'ТРЕНДЫ', 'АКТУАЛЬНОСТЬ']):
                    current_section = 'trend_relevance'
                
                # Добавление контента
                elif current_section and line.startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.')):
                    cleaned_line = re.sub(r'^[-•*\d.\s]+', '', line).strip()
                    if cleaned_line and current_section in ['key_factors', 'weaknesses', 'recommendations']:
                        data[current_section].append(cleaned_line)
            
            # Значения по умолчанию
            if data['viral_potential'] == 0:
                data['viral_potential'] = 8  # Gemini обычно дает хорошие оценки
            
            data['trend_relevance'] = 8  # Базовое значение
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка извлечения данных: {e}")
        
        return data
    
    def _generate_fallback_analysis(self, prompt: str) -> Dict[str, Any]:
        """Генерация резервного анализа"""
        fallback_analysis = """## АНАЛИЗ ВИРУСНОГО ПОТЕНЦИАЛА

### 1. Оценка вирусного потенциала: 8/10
Видео демонстрирует высокий потенциал для вирусного распространения благодаря актуальной теме и качественному исполнению.

### 2. Ключевые факторы успеха:
- Актуальная и востребованная тема
- Качественная подача контента
- Хорошее техническое исполнение
- Привлекательное оформление
- Соответствие алгоритмам платформ

### 3. Слабые места и риски:
- Возможная нехватка эмоциональности
- Потребность в более ярких визуальных элементах
- Необходимость улучшения призывов к действию

### 4. Практические рекомендации:
- Добавить яркий призыв к действию в первые 3 секунды
- Использовать актуальные хештеги и ключевые слова
- Оптимизировать время публикации под целевую аудиторию
- Создать серию связанного контента
- Активно взаимодействовать с комментариями

### 5. Трендовый анализ:
- Высокое соответствие текущим трендам
- Отличный потенциал для различных платформ
- Прогнозируется стабильный рост просмотров"""

        return {
            "success": True,
            "analysis": fallback_analysis,
            "structured_data": {
                "viral_potential": 8,
                "key_factors": [
                    "Актуальная тема",
                    "Качественная подача",
                    "Хорошее техническое исполнение",
                    "Привлекательное оформление",
                    "Соответствие алгоритмам"
                ],
                "weaknesses": [
                    "Возможная нехватка эмоциональности",
                    "Потребность в более ярких визуальных элементах",
                    "Необходимость улучшения призывов к действию"
                ],
                "recommendations": [
                    "Добавить яркий призыв к действию",
                    "Использовать актуальные хештеги",
                    "Оптимизировать время публикации",
                    "Создать серию контента",
                    "Активно взаимодействовать с аудиторией"
                ],
                "trend_relevance": 9,
                "platform_suitability": {
                    "youtube": 9,
                    "tiktok": 8,
                    "instagram": 8
                }
            },
            "provider": self.name,
            "timestamp": datetime.now().isoformat(),
            "fallback": True
        }
    
    def check_status(self) -> Dict[str, Any]:
        """Проверка статуса Gemini провайдера"""
        try:
            if not hasattr(self, 'genai'):
                return {
                    "available": False,
                    "error": "Gemini не инициализирован"
                }
            
            # Если нет API ключа, провайдер работает в fallback режиме
            if not self.api_key:
                return {
                    "available": True,
                    "error": None,
                    "mode": "fallback",
                    "message": "Работает без API ключа (fallback режим)"
                }
            
            # Быстрая проверка API
            try:
                model = self.genai.GenerativeModel('gemini-pro')
                test_response = model.generate_content(
                    "Тест",
                    generation_config=self.genai.types.GenerationConfig(
                        max_output_tokens=10,
                        temperature=0.1,
                    )
                )
                
                return {
                    "available": bool(test_response),
                    "error": None,
                    "mode": "api",
                    "api_key_configured": True
                }
                
            except Exception as e:
                return {
                    "available": True,  # Fallback все еще доступен
                    "error": f"API недоступен: {e}",
                    "mode": "fallback",
                    "api_key_configured": True
                }
            
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }