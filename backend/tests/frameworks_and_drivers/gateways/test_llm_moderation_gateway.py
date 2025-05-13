"""
Тесты для LLMModerationGateway.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import os
import httpx
from datetime import datetime

from src.entities.confession import Confession
from src.entities.enums import ConfessionStatus
from src.frameworks_and_drivers.gateways.llm_moderation_gateway import LLMModerationGateway


class TestLLMModerationGateway:
    """Тесты для LLMModerationGateway."""
    
    @pytest.fixture
    def confession(self):
        """Тестовое признание с нормальным содержимым."""
        return Confession(
            id=1,
            content="Тестовое нормальное признание для модерации",
            status=ConfessionStatus.PENDING,
        )
    
    @pytest.fixture
    def confession_with_forbidden_word(self):
        """Тестовое признание с запрещенным словом."""
        return Confession(
            id=2,
            content="Тестовое признание с bad словом для модерации",
            status=ConfessionStatus.PENDING,
        )
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {})  # Убираем API ключ из окружения
    async def test_moderate_mock_mode_approved(self, confession):
        """Тест для проверки модерации в режиме мока (одобрено)."""
        # Arrange
        gateway = LLMModerationGateway()
        
        # Act
        status = await gateway.moderate(confession)
        
        # Assert
        assert status == ConfessionStatus.APPROVED
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {})  # Убираем API ключ из окружения
    async def test_moderate_mock_mode_rejected(self, confession_with_forbidden_word):
        """Тест для проверки модерации в режиме мока (отклонено)."""
        # Arrange
        gateway = LLMModerationGateway()
        
        # Act
        status = await gateway.moderate(confession_with_forbidden_word)
        
        # Assert
        assert status == ConfessionStatus.REJECTED
        
        # Проверяем причину отклонения
        reason = await gateway.get_moderation_reason(confession_with_forbidden_word)
        assert reason is not None
        assert "bad" in reason
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"MODERATION_API_KEY": "fake_api_key"})
    @patch("httpx.AsyncClient.post")
    async def test_moderate_with_api_approved(self, mock_post, confession):
        """Тест для проверки модерации через API (одобрено)."""
        # Arrange
        # Имитируем успешный ответ от API
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "flagged": False,
                    "categories": {
                        "hate": False,
                        "sexual": False,
                        "violence": False,
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        gateway = LLMModerationGateway()
        
        # Act
        status = await gateway.moderate(confession)
        
        # Assert
        assert status == ConfessionStatus.APPROVED
        mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"MODERATION_API_KEY": "fake_api_key"})
    @patch("httpx.AsyncClient.post")
    async def test_moderate_with_api_rejected(self, mock_post, confession_with_forbidden_word):
        """Тест для проверки модерации через API (отклонено)."""
        # Arrange
        # Имитируем ответ от API с нарушениями
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "flagged": True,
                    "categories": {
                        "hate": True,
                        "sexual": False,
                        "violence": False,
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        gateway = LLMModerationGateway()
        
        # Act
        status = await gateway.moderate(confession_with_forbidden_word)
        
        # Assert
        assert status == ConfessionStatus.REJECTED
        mock_post.assert_called_once()
        
        # Проверяем причину отклонения
        reason = await gateway.get_moderation_reason(confession_with_forbidden_word)
        assert reason is not None
        assert "hate" in reason
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"MODERATION_API_KEY": "fake_api_key"})
    @patch("httpx.AsyncClient.post")
    async def test_moderate_with_api_error(self, mock_post, confession):
        """Тест для проверки обработки ошибок API."""
        # Arrange
        # Имитируем ошибку при запросе к API
        mock_post.side_effect = httpx.RequestError("Connection error")
        
        gateway = LLMModerationGateway()
        
        # Act
        status = await gateway.moderate(confession)
        
        # Assert
        # Если ошибка, то должны получить PENDING, чтобы потом проверить вручную
        assert status == ConfessionStatus.PENDING
        mock_post.assert_called_once() 