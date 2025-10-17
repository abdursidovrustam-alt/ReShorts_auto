"""Провайдер Google Gemini - бесплатный API от Google"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class GeminiProvider:
    """Провайдер Google Gemini"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "Google Gemini"
        self._init_client()
    
    def _init_client(self):
        """Инициализация клиента Gemini"""
        try:
            import google.generativeai as genai
            
            # Gemini бесплатен без API ключа для ограниченного использования
            # Или используем публичный доступ
            self.genai = genai
            self.model = genai.GenerativeModel('gemini-pro')
            
            logger.info("✅ Gemini клиент инициализирован")
        except ImportError:
            logger.error("❌ Библиотека google-generativeai не установлена")
            raise
    
    def generate(self, prompt: str, timeout: int = 30) -> str:
        """
        Генерация ответа через Gemini
        
        Args:
            prompt: Промпт для AI
            timeout: Таймаут в секундах
            
        Returns:
            Ответ от AI
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Ошибка Gemini: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Тест подключения"""
        try:
            result = self.generate("Hi", timeout=10)
            return bool(result)
        except:
            return False
