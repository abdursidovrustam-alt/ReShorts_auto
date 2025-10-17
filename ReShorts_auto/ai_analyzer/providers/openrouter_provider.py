"""Провайдер OpenRouter - доступ к DeepSeek и другим моделям"""

import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


class OpenRouterProvider:
    """Провайдер OpenRouter с бесплатным доступом к DeepSeek"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "OpenRouter"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        # DeepSeek бесплатен на OpenRouter
        self.model = "deepseek/deepseek-chat"
    
    def generate(self, prompt: str, timeout: int = 30) -> str:
        """
        Генерация ответа через OpenRouter
        
        Args:
            prompt: Промпт для AI
            timeout: Таймаут в секундах
            
        Returns:
            Ответ от AI
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(
                self.api_url,
                json=data,
                headers=headers,
                timeout=timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"Ошибка OpenRouter: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Тест подключения"""
        try:
            result = self.generate("Hi", timeout=10)
            return bool(result)
        except:
            return False
