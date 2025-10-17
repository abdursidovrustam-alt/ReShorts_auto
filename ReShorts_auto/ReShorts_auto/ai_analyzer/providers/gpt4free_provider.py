"""Провайдер GPT4Free - бесплатный доступ к различным AI моделям"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class GPT4FreeProvider:
    """Провайдер на основе библиотеки g4f (GPT4Free)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "GPT4Free"
        self._init_client()
    
    def _init_client(self):
        """Инициализация клиента g4f"""
        try:
            import g4f
            self.g4f = g4f
            self.client = g4f.Client()
            logger.info("✅ GPT4Free клиент инициализирован")
        except ImportError:
            logger.error("❌ Библиотека g4f не установлена. Установите: pip install g4f")
            raise
    
    def generate(self, prompt: str, timeout: int = 30) -> str:
        """
        Генерация ответа через GPT4Free
        
        Args:
            prompt: Промпт для AI
            timeout: Таймаут в секундах
            
        Returns:
            Ответ от AI
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Можно использовать gpt-4, claude и др.
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Ошибка GPT4Free: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Тест подключения"""
        try:
            result = self.generate("Hi", timeout=10)
            return bool(result)
        except:
            return False
