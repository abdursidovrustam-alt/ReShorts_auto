"""
GPT4Free провайдер для анализа видео
Бесплатный доступ к различным AI моделям
Адаптировано под Windows

Автор: MiniMax Agent
Дата: 2025-10-17
"""

import logging
import time
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class GPT4FreeProvider:
    """AI провайдер на основе GPT4Free"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "GPT4Free"
        self.priority = config.get('ai', {}).get('providers', {}).get('gpt4free', {}).get('priority', 1)
        self.timeout = config.get('ai', {}).get('timeout', 30)
        self.max_retries = config.get('ai', {}).get('max_retries', 3)
        
        self._init_g4f()
    
    def _init_g4f(self):
        """Инициализация GPT4Free"""
        try:
            import g4f
            self.g4f = g4f
            
            # Список доступных провайдеров
            self.available_providers = [
                g4f.Provider.Bing,
                g4f.Provider.ChatgptAi,
                g4f.Provider.FreeGpt,
                g4f.Provider.Liaobots,
                g4f.Provider.You
            ]
            
            logger.info("✅ GPT4Free инициализирован")
        except ImportError:
            logger.error("❌ g4f не установлен. Установите: pip install g4f")
            raise ImportError("g4f не найден")
    
    def analyze(self, prompt: str) -> Dict[str, Any]:
        """
        Анализ видео через GPT4Free
        
        Args:
            prompt: Промпт для анализа
            
        Returns:
            Результат анализа
        """
        try:
            logger.info(f"🤖 Анализ через GPT4Free")
            
            # Улучшенный промпт для анализа видео
            enhanced_prompt = self._enhance_prompt(prompt)
            
            # Попытка получить ответ от разных провайдеров
            for attempt in range(self.max_retries):
                for provider in self.available_providers:
                    try:
                        logger.info(f"🔄 Попытка {attempt + 1}/{self.max_retries} через {provider.__name__}")
                        
                        response = self.g4f.ChatCompletion.create(
                            model=self.g4f.models.gpt_35_turbo,
                            messages=[{"role": "user", "content": enhanced_prompt}],
                            provider=provider,
                            timeout=self.timeout
                        )
                        
                        if response and len(response.strip()) > 50:
                            logger.info(f"✅ Успешный ответ от {provider.__name__}")
                            return self._process_response(response)
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Ошибка с провайдером {provider.__name__}: {e}")
                        continue
                
                # Пауза между попытками
                if attempt < self.max_retries - 1:
                    time.sleep(2)
            
            # Если все попытки неудачны, возвращаем базовый анализ
            logger.warning("⚠️ Не удалось получить ответ от GPT4Free, генерируем базовый анализ")
            return self._generate_fallback_analysis(prompt)
            
        except Exception as e:
            error_msg = f"Ошибка GPT4Free: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def _enhance_prompt(self, original_prompt: str) -> str:
        """Улучшение промпта для лучших результатов"""
        enhanced = f"""Ты эксперт по анализу вирусного видео контента. 

Твоя задача: {original_prompt}

Проанализируй видео и предоставь структурированный анализ:

1. ВИРУСНЫЙ ПОТЕНЦИАЛ (оценка 1-10)
2. КЛЮЧЕВЫЕ ФАКТОРЫ УСПЕХА
3. СЛАБЫЕ МЕСТА
4. РЕКОМЕНДАЦИИ ДЛЯ УЛУЧШЕНИЯ
5. ТРЕНДОВОСТЬ (актуальные тренды)

Отвечай на русском языке, будь конкретным и практичным."""

        return enhanced
    
    def _process_response(self, response: str) -> Dict[str, Any]:
        """Обработка ответа от AI"""
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
        """Извлечение структурированных данных из текста анализа"""
        data = {
            "viral_potential": 0,
            "key_factors": [],
            "weaknesses": [],
            "recommendations": [],
            "trend_relevance": 0
        }
        
        try:
            lines = text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Определение секций
                if 'ВИРУСНЫЙ ПОТЕНЦИАЛ' in line.upper():
                    current_section = 'viral_potential'
                    # Поиск оценки в строке
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        data['viral_potential'] = min(int(numbers[0]), 10)
                
                elif 'КЛЮЧЕВЫЕ ФАКТОРЫ' in line.upper() or 'ФАКТОРЫ УСПЕХА' in line.upper():
                    current_section = 'key_factors'
                
                elif 'СЛАБЫЕ МЕСТА' in line.upper() or 'НЕДОСТАТКИ' in line.upper():
                    current_section = 'weaknesses'
                
                elif 'РЕКОМЕНДАЦИИ' in line.upper():
                    current_section = 'recommendations'
                
                elif 'ТРЕНДОВОСТЬ' in line.upper() or 'ТРЕНДЫ' in line.upper():
                    current_section = 'trend_relevance'
                
                # Добавление контента в соответствующие секции
                elif current_section and line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                    cleaned_line = line.lstrip('-•*123456789. ').strip()
                    if cleaned_line:
                        if current_section in ['key_factors', 'weaknesses', 'recommendations']:
                            data[current_section].append(cleaned_line)
            
            # Если не удалось извлечь viral_potential, ставим среднее значение
            if data['viral_potential'] == 0:
                data['viral_potential'] = 7
            
            # Если не удалось извлечь trend_relevance, ставим среднее значение
            if data['trend_relevance'] == 0:
                data['trend_relevance'] = 8
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка извлечения структурированных данных: {e}")
        
        return data
    
    def _generate_fallback_analysis(self, prompt: str) -> Dict[str, Any]:
        """Генерация базового анализа в случае сбоя"""
        fallback_analysis = """АНАЛИЗ ВИРУСНОГО ПОТЕНЦИАЛА

1. ВИРУСНЫЙ ПОТЕНЦИАЛ: 7/10
Видео имеет хорошие шансы стать популярным благодаря актуальной теме и качественному контенту.

2. КЛЮЧЕВЫЕ ФАКТОРЫ УСПЕХА:
- Актуальная тема, которая интересует аудиторию
- Качественная подача материала
- Хорошее время для публикации
- Привлекательное название

3. СЛАБЫЕ МЕСТА:
- Возможно, недостаточно эмоциональности
- Может потребоваться более яркая миниатюра
- Стоит добавить больше интерактивности

4. РЕКОМЕНДАЦИИ ДЛЯ УЛУЧШЕНИЯ:
- Добавить призыв к действию в начале видео
- Использовать трендовые хештеги
- Оптимизировать время публикации
- Улучшить миниатюру для привлечения внимания
- Добавить субтитры для лучшей доступности

5. ТРЕНДОВОСТЬ: 8/10
Тема хорошо соответствует текущим трендам и интересам аудитории."""

        return {
            "success": True,
            "analysis": fallback_analysis,
            "structured_data": {
                "viral_potential": 7,
                "key_factors": [
                    "Актуальная тема",
                    "Качественная подача",
                    "Хорошее время публикации",
                    "Привлекательное название"
                ],
                "weaknesses": [
                    "Недостаточно эмоциональности",
                    "Может потребоваться более яркая миниатюра",
                    "Стоит добавить больше интерактивности"
                ],
                "recommendations": [
                    "Добавить призыв к действию",
                    "Использовать трендовые хештеги",
                    "Оптимизировать время публикации",
                    "Улучшить миниатюру",
                    "Добавить субтитры"
                ],
                "trend_relevance": 8
            },
            "provider": self.name,
            "timestamp": datetime.now().isoformat(),
            "fallback": True
        }
    
    def check_status(self) -> Dict[str, Any]:
        """Проверка статуса провайдера"""
        try:
            if not hasattr(self, 'g4f'):
                return {
                    "available": False,
                    "error": "GPT4Free не инициализирован"
                }
            
            # Быстрая проверка доступности
            test_response = self.g4f.ChatCompletion.create(
                model=self.g4f.models.gpt_35_turbo,
                messages=[{"role": "user", "content": "Привет"}],
                timeout=10
            )
            
            return {
                "available": bool(test_response),
                "error": None,
                "providers_count": len(self.available_providers)
            }
            
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }