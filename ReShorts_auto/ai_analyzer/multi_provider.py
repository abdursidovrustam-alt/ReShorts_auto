"""
Универсальный AI-модуль с поддержкой нескольких провайдеров
Поддерживает: GPT4Free, OpenRouter, Google Gemini, LocalAI
Автоматическое переключение между провайдерами при ошибках
"""

import logging
import json
import time
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class AIProviderManager:
    """Менеджер AI провайдеров с автоматическим fallback"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = []
        self.current_provider_index = 0
        self.cache = {} if config.get('ai', {}).get('cache_enabled', True) else None
        
        # Инициализация провайдеров в порядке приоритета
        self._init_providers()
        
    def _init_providers(self):
        """Инициализация доступных AI провайдеров"""
        ai_config = self.config.get('ai', {})
        providers_config = ai_config.get('providers', {})
        
        # GPT4Free
        if providers_config.get('gpt4free', {}).get('enabled', True):
            try:
                from .providers.gpt4free_provider import GPT4FreeProvider
                self.providers.append(GPT4FreeProvider(ai_config))
                logger.info("✅ GPT4Free провайдер инициализирован")
            except Exception as e:
                logger.warning(f"⚠️ GPT4Free провайдер недоступен: {e}")
        
        # OpenRouter (DeepSeek)
        if providers_config.get('openrouter', {}).get('enabled', True):
            try:
                from .providers.openrouter_provider import OpenRouterProvider
                self.providers.append(OpenRouterProvider(ai_config))
                logger.info("✅ OpenRouter провайдер инициализирован")
            except Exception as e:
                logger.warning(f"⚠️ OpenRouter провайдер недоступен: {e}")
        
        # Google Gemini
        if providers_config.get('gemini', {}).get('enabled', True):
            try:
                from .providers.gemini_provider import GeminiProvider
                self.providers.append(GeminiProvider(ai_config))
                logger.info("✅ Gemini провайдер инициализирован")
            except Exception as e:
                logger.warning(f"⚠️ Gemini провайдер недоступен: {e}")
        
        # LocalAI (опционально)
        if providers_config.get('localai', {}).get('enabled', False):
            try:
                from .providers.localai_provider import LocalAIProvider
                self.providers.append(LocalAIProvider(ai_config))
                logger.info("✅ LocalAI провайдер инициализирован")
            except Exception as e:
                logger.warning(f"⚠️ LocalAI провайдер недоступен: {e}")
        
        if not self.providers:
            logger.error("❌ Ни один AI провайдер не доступен!")
            raise RuntimeError("Нет доступных AI провайдеров")
        
        logger.info(f"📊 Инициализировано {len(self.providers)} AI провайдеров")
    
    def _get_cache_key(self, prompt: str) -> str:
        """Создание ключа кэша"""
        import hashlib
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def analyze_video(self, video_data: Dict[str, Any], prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Анализ видео с использованием AI
        
        Args:
            video_data: Данные о видео (метаданные, транскрипт и т.д.)
            prompt: Опциональный промпт для анализа
            
        Returns:
            Результаты анализа
        """
        # Формирование промпта
        if not prompt:
            prompt = self._create_default_prompt(video_data)
        
        # Проверка кэша
        if self.cache is not None:
            cache_key = self._get_cache_key(prompt)
            if cache_key in self.cache:
                logger.info("📦 Результат получен из кэша")
                return self.cache[cache_key]
        
        # Попытка выполнить запрос с fallback
        result = self._execute_with_fallback(prompt)
        
        # Сохранение в кэш
        if self.cache is not None and result:
            self.cache[cache_key] = result
        
        return result
    
    def _create_default_prompt(self, video_data: Dict[str, Any]) -> str:
        """Создание промпта по умолчанию для анализа видео"""
        title = video_data.get('title', 'Без названия')
        description = video_data.get('description', '')[:500]  # Первые 500 символов
        
        prompt = f"""Проанализируй это видео и определи его вирусный потенциал.

Название: {title}
Описание: {description}

Оцени следующие параметры (от 1 до 10):
1. Вирусный потенциал
2. Эмоциональное воздействие
3. Уникальность контента
4. Качество производства
5. Целевая аудитория

Также определи:
- Основные темы и ключевые слова
- Рекомендуемые хештеги
- Лучшее время для публикации
- Предложения по улучшению

Ответ предоставь в формате JSON."""
        
        return prompt
    
    def _execute_with_fallback(self, prompt: str) -> Dict[str, Any]:
        """
        Выполнение запроса с автоматическим переключением между провайдерами
        
        Args:
            prompt: Промпт для AI
            
        Returns:
            Результат анализа
        """
        max_retries = self.config.get('ai', {}).get('max_retries', 3)
        timeout = self.config.get('ai', {}).get('timeout', 30)
        
        # Пробуем каждый провайдер
        for attempt in range(max_retries):
            for i, provider in enumerate(self.providers):
                try:
                    logger.info(f"🤖 Попытка {attempt + 1}/{max_retries} с провайдером: {provider.name}")
                    
                    result = provider.generate(prompt, timeout=timeout)
                    
                    if result:
                        logger.info(f"✅ Успешный ответ от {provider.name}")
                        return self._parse_response(result)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка с {provider.name}: {e}")
                    continue
            
            # Небольшая пауза перед следующей попыткой
            if attempt < max_retries - 1:
                time.sleep(2)
        
        logger.error("❌ Все AI провайдеры недоступны")
        return {
            "error": "Все AI провайдеры недоступны",
            "viral_score": 0,
            "analysis": "Анализ недоступен"
        }
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Парсинг ответа от AI"""
        try:
            # Попытка распарсить как JSON
            if isinstance(response, str):
                # Ищем JSON в тексте
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return response if isinstance(response, dict) else {"analysis": response}
        
        except Exception as e:
            logger.warning(f"Ошибка парсинга ответа: {e}")
            return {"analysis": response}
    
    def get_provider_status(self) -> List[Dict[str, Any]]:
        """Получение статуса всех провайдеров"""
        status = []
        for provider in self.providers:
            try:
                is_available = provider.test_connection()
                status.append({
                    "name": provider.name,
                    "available": is_available,
                    "priority": self.providers.index(provider) + 1
                })
            except:
                status.append({
                    "name": provider.name,
                    "available": False,
                    "priority": self.providers.index(provider) + 1
                })
        return status


class BaseAIProvider:
    """Базовый класс для AI провайдеров"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "BaseProvider"
    
    def generate(self, prompt: str, timeout: int = 30) -> str:
        """Генерация ответа от AI"""
        raise NotImplementedError
    
    def test_connection(self) -> bool:
        """Тест подключения к провайдеру"""
        try:
            response = self.generate("Test", timeout=5)
            return bool(response)
        except:
            return False
