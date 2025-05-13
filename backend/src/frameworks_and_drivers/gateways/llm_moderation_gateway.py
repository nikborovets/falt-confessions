"""
Гейтвей для работы с системой модерации на базе LLM.
"""
import os
from typing import Optional

import httpx
from loguru import logger

from src.entities.confession import Confession
from src.entities.enums import ConfessionStatus
from src.interface_adapters.gateway_protocols import ModerationGatewayProtocol


class LLMModerationGateway(ModerationGatewayProtocol):
    """Реализация гейтвея для работы с системой модерации на базе LLM."""
    
    def __init__(self) -> None:
        """Инициализация клиента для API модерации."""
        self._api_key = os.getenv("MODERATION_API_KEY")
        self._api_url = os.getenv("MODERATION_API_URL", "https://api.openai.com/v1/moderations")
        
        if not self._api_key:
            logger.warning("MODERATION_API_KEY not set, using mock implementation")
        
        # Сохраняем причины отклонения для последующего получения
        self._rejection_reasons = {}
    
    async def moderate(self, confession: Confession) -> ConfessionStatus:
        """
        Проводит модерацию признания с помощью LLM.
        
        Args:
            confession: Доменная сущность признания
            
        Returns:
            ConfessionStatus: Статус признания после модерации (APPROVED/REJECTED)
        """
        if not self._api_key:
            # Mock-реализация для тестирования
            logger.info(f"Mock: Moderating confession: {confession.content[:50]}...")
            
            # Простая заглушка: отклоняем, если содержит ключевые слова
            forbidden_words = ["bad", "offensive", "inappropriate", "hate"]
            
            for word in forbidden_words:
                if word in confession.content.lower():
                    self._rejection_reasons[confession.id] = f"Content contains forbidden word: '{word}'"
                    return ConfessionStatus.REJECTED
            
            return ConfessionStatus.APPROVED
        
        try:
            # Формируем запрос к API модерации
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            }
            
            data = {
                "input": confession.content,
            }
            
            # Отправляем запрос
            async with httpx.AsyncClient() as client:
                response = await client.post(self._api_url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
            
            # Анализируем результат
            if result["results"][0]["flagged"]:
                # Сохраняем категории нарушений
                categories = result["results"][0]["categories"]
                flagged_categories = [
                    category for category, flagged in categories.items() if flagged
                ]
                
                self._rejection_reasons[confession.id] = (
                    f"Content flagged for: {', '.join(flagged_categories)}"
                )
                
                logger.info(f"Confession {confession.id} rejected: {self._rejection_reasons[confession.id]}")
                return ConfessionStatus.REJECTED
            
            logger.info(f"Confession {confession.id} approved by moderation system")
            return ConfessionStatus.APPROVED
        
        except Exception as e:
            logger.error(f"Error during moderation: {str(e)}")
            # В случае ошибки лучше отправить на ручную модерацию
            return ConfessionStatus.PENDING
    
    async def get_moderation_reason(self, confession: Confession) -> Optional[str]:
        """
        Получает причину отклонения признания при модерации.
        
        Args:
            confession: Доменная сущность признания
            
        Returns:
            Optional[str]: Причина отклонения или None, если признание одобрено
        """
        if confession.id in self._rejection_reasons:
            return self._rejection_reasons[confession.id]
        
        return None 