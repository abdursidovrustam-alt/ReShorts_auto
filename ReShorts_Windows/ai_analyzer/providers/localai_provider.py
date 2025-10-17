"""
LocalAI провайдер для анализа видео
Локальный AI сервер для приватности
Адаптировано под Windows

Автор: MiniMax Agent
Дата: 2025-10-17
"""

import logging
import requests
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class LocalAIProvider:
    """AI провайдер на основе LocalAI"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "LocalAI"
        localai_config = config.get('ai', {}).get('providers', {}).get('localai', {})
        self.priority = localai_config.get('priority', 4)
        self.timeout = localai_config.get('timeout', 15)
        self.url = localai_config.get('url', 'http://localhost:8080')
        self.model = localai_config.get('model', 'gpt-3.5-turbo')
        
        logger.info(f"LocalAI настроен: {self.url}")
    
    def analyze(self, prompt: str) -> Dict[str, Any]:
        """
        Анализ видео через LocalAI
        
        Args:
            prompt: Промпт для анализа
            
        Returns:
            Результат анализа
        """
        try:
            logger.info(f"🤖 Анализ через LocalAI ({self.model})")
            
            enhanced_prompt = self._enhance_prompt(prompt)
            
            headers = {
                'Content-Type': 'application/json'
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
                'temperature': 0.7,
                'stream': False
            }
            
            response = requests.post(
                f'{self.url}/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('choices') and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    logger.info("✅ Успешный ответ от LocalAI")
                    return self._process_response(content)
                else:
                    logger.warning("⚠️ Пустой ответ от LocalAI")
                    return self._generate_fallback_analysis(prompt)
            else:
                logger.warning(f"⚠️ Ошибка LocalAI API: {response.status_code}")
                return self._generate_fallback_analysis(prompt)
                
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️ LocalAI сервер недоступен")
            return self._generate_fallback_analysis(prompt)
        except Exception as e:
            logger.warning(f"⚠️ Ошибка LocalAI: {e}")
            return self._generate_fallback_analysis(prompt)
    
    def _enhance_prompt(self, original_prompt: str) -> str:
        """Улучшение промпта для LocalAI"""
        enhanced = f"""Ты профессиональный аналитик вирусного контента.

Задача: {original_prompt}

Предоставь структурированный анализ:

# АНАЛИЗ ВИРУСНОГО ПОТЕНЦИАЛА

## 1. Вирусный потенциал (1-10)
Оцени шансы стать вирусным

## 2. Ключевые факторы успеха
- Что работает в контенте
- Сильные стороны

## 3. Слабые места
- Что нужно улучшить
- Потенциальные проблемы

## 4. Рекомендации
- Конкретные шаги улучшения
- Советы по продвижению

## 5. Актуальность трендов
- Соответствие трендам
- Прогноз популярности

Отвечай кратко и по делу на русском языке."""

        return enhanced
    
    def _process_response(self, response: str) -> Dict[str, Any]:
        """Обработка ответа от LocalAI"""
        try:
            cleaned_response = response.strip()
            analysis_data = self._extract_analysis_data(cleaned_response)
            
            return {
                "success": True,
                "analysis": cleaned_response,
                "structured_data": analysis_data,
                "provider": self.name,
                "model": self.model,
                "server": self.url,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки ответа LocalAI: {e}")
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
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        data['viral_potential'] = min(int(numbers[0]), 10)
                
                elif any(keyword in line.upper() for keyword in ['КЛЮЧЕВЫЕ ФАКТОРЫ', 'ФАКТОРЫ', 'СИЛЬНЫЕ']):
                    current_section = 'key_factors'
                
                elif any(keyword in line.upper() for keyword in ['СЛАБЫЕ', 'ПРОБЛЕМЫ', 'НЕДОСТАТКИ']):
                    current_section = 'weaknesses'
                
                elif any(keyword in line.upper() for keyword in ['РЕКОМЕНДАЦИИ', 'СОВЕТЫ']):
                    current_section = 'recommendations'
                
                elif any(keyword in line.upper() for keyword in ['АКТУАЛЬНОСТЬ', 'ТРЕНДЫ']):
                    current_section = 'trend_relevance'
                
                # Добавление контента
                elif current_section and line.startswith(('-', '•', '*', '1.', '2.')):
                    cleaned_line = re.sub(r'^[-•*\d.\s]+', '', line).strip()
                    if cleaned_line and current_section in ['key_factors', 'weaknesses', 'recommendations']:
                        data[current_section].append(cleaned_line)
            
            # Значения по умолчанию
            if data['viral_potential'] == 0:
                data['viral_potential'] = 7
            
            data['trend_relevance'] = 7
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка извлечения данных: {e}")
        
        return data
    
    def _generate_fallback_analysis(self, prompt: str) -> Dict[str, Any]:
        """Генерация резервного анализа"""
        fallback_analysis = """# АНАЛИЗ ВИРУСНОГО ПОТЕНЦИАЛА

## 1. Вирусный потенциал: 7/10
Контент имеет хорошие шансы стать популярным при правильном продвижении.

## 2. Ключевые факторы успеха:
- Актуальная тема
- Качественное исполнение
- Подходящий формат
- Целевая аудитория

## 3. Слабые места:
- Нужно больше эмоций
- Улучшить превью
- Добавить интерактивность

## 4. Рекомендации:
- Добавить призыв к действию
- Использовать хештеги
- Оптимизировать время публикации
- Создать серию контента

## 5. Актуальность трендов: 7/10
Тема соответствует текущим интересам аудитории."""

        return {
            "success": True,
            "analysis": fallback_analysis,
            "structured_data": {
                "viral_potential": 7,
                "key_factors": [
                    "Актуальная тема",
                    "Качественное исполнение",
                    "Подходящий формат",
                    "Целевая аудитория"
                ],
                "weaknesses": [
                    "Нужно больше эмоций",
                    "Улучшить превью",
                    "Добавить интерактивность"
                ],
                "recommendations": [
                    "Добавить призыв к действию",
                    "Использовать хештеги",
                    "Оптимизировать время публикации",
                    "Создать серию контента"
                ],
                "trend_relevance": 7
            },
            "provider": self.name,
            "model": "fallback",
            "server": self.url,
            "timestamp": datetime.now().isoformat(),
            "fallback": True
        }
    
    def check_status(self) -> Dict[str, Any]:
        """Проверка статуса LocalAI провайдера"""
        try:
            response = requests.get(
                f'{self.url}/v1/models',
                timeout=5
            )
            
            available = response.status_code == 200
            
            if available:
                models = response.json().get('data', [])
                available_models = [model.get('id', '') for model in models]
                model_available = self.model in available_models
                
                return {
                    "available": model_available,
                    "error": None if model_available else f"Модель {self.model} недоступна",
                    "server": self.url,
                    "model": self.model,
                    "available_models": available_models[:5]  # Первые 5 моделей
                }
            else:
                return {
                    "available": False,
                    "error": f"Сервер недоступен (HTTP {response.status_code})",
                    "server": self.url,
                    "model": self.model
                }
            
        except requests.exceptions.ConnectionError:
            return {
                "available": False,
                "error": "Соединение отклонено (сервер не запущен?)",
                "server": self.url,
                "model": self.model
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "server": self.url,
                "model": self.model
            }