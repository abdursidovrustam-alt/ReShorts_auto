"""
Менеджер AI провайдеров для анализа видео
Поддержка: GPT4Free, Google Gemini, OpenRouter, LocalAI
Адаптировано под Windows

Автор: MiniMax Agent
Дата: 2025-10-17
"""

import logging
import time
from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class AIProviderManager:
    """Менеджер AI провайдеров для анализа видео контента"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ai_config = config.get('ai', {})
        self.providers = []
        self.cache = {}
        self.cache_enabled = self.ai_config.get('cache_enabled', True)
        
        self._init_providers()
    
    def _init_providers(self):
        """Инициализация AI провайдеров"""
        providers_config = self.ai_config.get('providers', {})
        
        # GPT4Free (бесплатный)
        if providers_config.get('gpt4free', {}).get('enabled', True):
            try:
                from ai_analyzer.providers.gpt4free_provider import GPT4FreeProvider
                provider = GPT4FreeProvider(self.config)
                self.providers.append(provider)
                logger.info("✅ GPT4Free провайдер инициализирован")
            except Exception as e:
                logger.warning(f"⚠️ GPT4Free недоступен: {e}")
        
        # Google Gemini (бесплатный)
        if providers_config.get('gemini', {}).get('enabled', True):
            try:
                from ai_analyzer.providers.gemini_provider import GeminiProvider
                provider = GeminiProvider(self.config)
                self.providers.append(provider)
                logger.info("✅ Gemini провайдер инициализирован")
            except Exception as e:
                logger.warning(f"⚠️ Gemini недоступен: {e}")
        
        # OpenRouter (платный, опционально)
        if providers_config.get('openrouter', {}).get('enabled', False):
            try:
                from ai_analyzer.providers.openrouter_provider import OpenRouterProvider
                provider = OpenRouterProvider(self.config)
                self.providers.append(provider)
                logger.info("✅ OpenRouter провайдер инициализирован")
            except Exception as e:
                logger.warning(f"⚠️ OpenRouter недоступен: {e}")
        
        # LocalAI (локальный, опционально)
        if providers_config.get('localai', {}).get('enabled', False):
            try:
                from ai_analyzer.providers.localai_provider import LocalAIProvider
                provider = LocalAIProvider(self.config)
                self.providers.append(provider)
                logger.info("✅ LocalAI провайдер инициализирован")
            except Exception as e:
                logger.warning(f"⚠️ LocalAI недоступен: {e}")
        
        # Сортировка по приоритету
        self.providers.sort(key=lambda p: p.priority)
        
        if not self.providers:
            logger.error("❌ Нет доступных AI провайдеров!")
    
    def analyze(self, video_data: Any, prompt: str = "") -> Dict[str, Any]:
        """
        Анализ видео данных с помощью AI
        
        Args:
            video_data: Данные видео (dict, str или JSON)
            prompt: Дополнительный промпт для анализа
            
        Returns:
            Результат анализа
        """
        try:
            # Подготовка данных
            if isinstance(video_data, str):
                try:
                    video_data = json.loads(video_data)
                except json.JSONDecodeError:
                    # Если не JSON, оставляем как строку
                    pass
            
            # Создание полного промпта
            full_prompt = self._create_analysis_prompt(video_data, prompt)
            
            # Проверка кеша
            cache_key = self._get_cache_key(full_prompt)
            if self.cache_enabled and cache_key in self.cache:
                logger.info("💾 Результат получен из кеша")
                return self.cache[cache_key]
            
            logger.info("🤖 Начало AI анализа видео")
            
            # Попытка анализа через доступные провайдеры
            last_error = None
            for provider in self.providers:
                try:
                    logger.info(f"🔄 Попытка анализа через {provider.name}")
                    result = provider.analyze(full_prompt)
                    
                    if result.get('success'):
                        logger.info(f"✅ Анализ выполнен через {provider.name}")
                        
                        # Обогащение результата
                        enriched_result = self._enrich_analysis_result(result, video_data, provider.name)
                        
                        # Сохранение в кеш
                        if self.cache_enabled:
                            self.cache[cache_key] = enriched_result
                        
                        return enriched_result
                    else:
                        last_error = result.get('error', 'Неизвестная ошибка')
                        logger.warning(f"⚠️ {provider.name}: {last_error}")
                        
                except Exception as e:
                    last_error = str(e)
                    logger.error(f"❌ Ошибка в {provider.name}: {e}")
                    continue
            
            # Если все провайдеры не сработали
            error_msg = f"Не удалось выполнить анализ. Последняя ошибка: {last_error}"
            logger.error(f"❌ {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Критическая ошибка анализа: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_analysis_prompt(self, video_data: Any, custom_prompt: str = "") -> str:
        """Создание промпта для анализа"""
        base_prompt = self.ai_config.get('default_prompt', 
            "Проанализируй это видео и объясни, почему оно может быть вирусным.")
        
        # Формирование данных о видео
        if isinstance(video_data, dict):
            video_info = []
            
            if video_data.get('title'):
                video_info.append(f"Заголовок: {video_data['title']}")
            
            if video_data.get('description'):
                desc = str(video_data['description'])[:500]  # Ограничиваем длину
                video_info.append(f"Описание: {desc}")
            
            if video_data.get('views'):
                video_info.append(f"Просмотры: {video_data['views']:,}")
            
            if video_data.get('likes'):
                video_info.append(f"Лайки: {video_data['likes']:,}")
            
            if video_data.get('comments'):
                video_info.append(f"Комментарии: {video_data['comments']:,}")
            
            if video_data.get('duration'):
                video_info.append(f"Длительность: {video_data['duration']} сек")
            
            if video_data.get('platform'):
                video_info.append(f"Платформа: {video_data['platform']}")
            
            if video_data.get('viral_score'):
                video_info.append(f"Viral Score: {video_data['viral_score']}")
            
            video_text = "\n".join(video_info)
        else:
            video_text = str(video_data)
        
        # Объединение промптов
        if custom_prompt:
            full_prompt = f"{custom_prompt}\n\nДанные видео:\n{video_text}"
        else:
            full_prompt = f"{base_prompt}\n\nДанные видео:\n{video_text}"
        
        return full_prompt
    
    def _enrich_analysis_result(self, result: Dict[str, Any], video_data: Any, provider_name: str) -> Dict[str, Any]:
        """Обогащение результата анализа дополнительными данными"""
        enriched = result.copy()
        
        # Добавление метаданных
        enriched.update({
            "provider": provider_name,
            "timestamp": datetime.now().isoformat(),
            "video_metadata": self._extract_video_metadata(video_data)
        })
        
        # Добавление рекомендаций если их нет
        if 'recommendations' not in enriched:
            enriched['recommendations'] = self._generate_basic_recommendations(video_data)
        
        # Добавление оценок если их нет
        if 'scores' not in enriched:
            enriched['scores'] = self._generate_basic_scores(video_data)
        
        return enriched
    
    def _extract_video_metadata(self, video_data: Any) -> Dict[str, Any]:
        """Извлечение метаданных видео"""
        if not isinstance(video_data, dict):
            return {}
        
        return {
            "platform": video_data.get('platform', 'unknown'),
            "duration": video_data.get('duration', 0),
            "views": video_data.get('views', 0),
            "engagement_rate": self._calculate_engagement_rate(video_data),
            "viral_score": video_data.get('viral_score', 0)
        }
    
    def _calculate_engagement_rate(self, video_data: Dict[str, Any]) -> float:
        """Расчет engagement rate"""
        views = video_data.get('views', 0)
        likes = video_data.get('likes', 0)
        comments = video_data.get('comments', 0)
        
        if views == 0:
            return 0
        
        return round((likes + comments) / views * 100, 2)
    
    def _generate_basic_recommendations(self, video_data: Any) -> List[str]:
        """Генерация базовых рекомендаций"""
        recommendations = [
            "Используйте трендовые хештеги",
            "Оптимизируйте время публикации",
            "Добавьте призыв к действию",
            "Используйте качественные миниатюры"
        ]
        
        if isinstance(video_data, dict):
            duration = video_data.get('duration', 0)
            if duration > 60:
                recommendations.append("Сократите длительность видео до 15-60 секунд")
            
            engagement = self._calculate_engagement_rate(video_data)
            if engagement < 5:
                recommendations.append("Улучшите вовлеченность аудитории")
        
        return recommendations
    
    def _generate_basic_scores(self, video_data: Any) -> Dict[str, float]:
        """Генерация базовых оценок"""
        scores = {
            "viral_potential": 7.5,
            "content_quality": 8.0,
            "engagement_quality": 7.0,
            "trend_relevance": 8.5
        }
        
        if isinstance(video_data, dict):
            viral_score = video_data.get('viral_score', 0)
            if viral_score > 0:
                scores["viral_potential"] = min(viral_score / 10, 10)
        
        return scores
    
    def _get_cache_key(self, prompt: str) -> str:
        """Создание ключа для кеша"""
        import hashlib
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса всех AI провайдеров"""
        status = {}
        
        for provider in self.providers:
            try:
                provider_status = provider.check_status()
                status[provider.name] = {
                    "available": provider_status.get('available', False),
                    "error": provider_status.get('error'),
                    "priority": provider.priority,
                    "last_used": getattr(provider, 'last_used', None)
                }
            except Exception as e:
                status[provider.name] = {
                    "available": False,
                    "error": str(e),
                    "priority": getattr(provider, 'priority', 999)
                }
        
        return status
    
    def clear_cache(self):
        """Очистка кеша"""
        self.cache.clear()
        logger.info("🗑️ Кеш AI анализов очищен")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кеша"""
        return {
            "enabled": self.cache_enabled,
            "size": len(self.cache),
            "memory_usage": sum(len(str(v)) for v in self.cache.values())
        }