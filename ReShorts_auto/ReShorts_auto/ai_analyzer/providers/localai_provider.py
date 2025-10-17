"""Провайдер LocalAI - локальная AI модель"""

import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


class LocalAIProvider:
    """Провайдер для локальной AI модели (LocalAI, Ollama и т.д.)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "LocalAI"
        # URL локального AI сервера
        self.api_url = config.get('ai', {}).get('providers', {}).get('localai', {}).get('url', 'http://localhost:8080')
        self.model = config.get('ai', {}).get('providers', {}).get('localai', {}).get('model', 'gpt-3.5-turbo')
    
    def generate(self, prompt: str, timeout: int = 30) -> str:
        """
        Генерация ответа через LocalAI
        
        Args:
            prompt: Промпт для AI
            timeout: Таймаут в секундах
            
        Returns:
            Ответ от AI
        """
        try:
            url = f"{self.api_url}/v1/chat/completions"
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(
                url,
                json=data,
                timeout=timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"Ошибка LocalAI: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Тест подключения"""
        try:
            result = self.generate("Hi", timeout=10)
            return bool(result)
        except:
            return False
