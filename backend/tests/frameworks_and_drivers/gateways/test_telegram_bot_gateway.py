"""
Тесты для TelegramBotGateway.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import os
from datetime import datetime

from src.entities.confession import Confession, Poll, PollOption, Tag
from src.entities.enums import ConfessionStatus
from src.frameworks_and_drivers.gateways.telegram_bot_gateway import TelegramBotGateway


class TestTelegramBotGateway:
    """Тесты для TelegramBotGateway."""
    
    @pytest.fixture
    def mock_bot(self):
        """Мок объекта Telegram-бота."""
        bot_mock = AsyncMock()
        bot_mock.send_message.return_value = MagicMock(message_id="123456")
        bot_mock.send_poll.return_value = MagicMock(message_id="654321")
        return bot_mock
    
    @pytest.fixture
    def confession(self):
        """Тестовое признание."""
        return Confession(
            id=1,
            content="Тестовое признание для Telegram",
            status=ConfessionStatus.APPROVED,
            tags=[
                Tag(name="тест"),
                Tag(name="telegram"),
            ]
        )
    
    @pytest.fixture
    def confession_with_poll(self, confession):
        """Тестовое признание с опросом."""
        confession_with_poll = Confession(
            id=2,
            content="Тестовое признание с опросом",
            status=ConfessionStatus.APPROVED,
            poll=Poll(
                question="Тестовый вопрос",
                options=[
                    PollOption(text="Вариант 1"),
                    PollOption(text="Вариант 2"),
                ],
            )
        )
        return confession_with_poll
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "fake_token"})
    @patch("src.frameworks_and_drivers.gateways.telegram_bot_gateway.Bot")
    async def test_send_confession(self, mock_bot_class, mock_bot, confession):
        """Тест отправки признания в Telegram."""
        # Arrange
        mock_bot_class.return_value = mock_bot
        gateway = TelegramBotGateway()
        
        # Act
        message_id = await gateway.send_confession(confession)
        
        # Assert
        assert message_id == "123456"
        mock_bot.send_message.assert_called_once()
        # Проверяем, что в сообщении есть теги и контент
        call_args = mock_bot.send_message.call_args[1]
        assert "#1" in call_args["text"]
        assert "Тестовое признание" in call_args["text"]
        assert "#тест" in call_args["text"]
        assert "#telegram" in call_args["text"]
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "fake_token"})
    @patch("src.frameworks_and_drivers.gateways.telegram_bot_gateway.Bot")
    async def test_send_poll(self, mock_bot_class, mock_bot, confession_with_poll):
        """Тест отправки опроса в Telegram."""
        # Arrange
        mock_bot_class.return_value = mock_bot
        gateway = TelegramBotGateway()
        
        # Act
        poll_message_id = await gateway.send_poll(confession_with_poll.poll)
        
        # Assert
        assert poll_message_id == "654321"
        mock_bot.send_poll.assert_called_once()
        # Проверяем, что в опросе корректные данные
        call_args = mock_bot.send_poll.call_args[1]
        assert call_args["question"] == "Тестовый вопрос"
        assert len(call_args["options"]) == 2
        assert call_args["options"][0] == "Вариант 1"
        assert call_args["options"][1] == "Вариант 2"
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {})  # Убираем токен из окружения
    async def test_mock_mode_when_no_token(self, confession):
        """Тест работы в режиме мока, когда токен не установлен."""
        # Arrange
        gateway = TelegramBotGateway()
        
        # Act
        message_id = await gateway.send_confession(confession)
        
        # Assert
        assert message_id == "mock_message_id"
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {})  # Убираем токен из окружения
    async def test_mock_mode_for_poll(self, confession_with_poll):
        """Тест работы в режиме мока для опроса, когда токен не установлен."""
        # Arrange
        gateway = TelegramBotGateway()
        
        # Act
        poll_message_id = await gateway.send_poll(confession_with_poll.poll)
        
        # Assert
        assert poll_message_id == "mock_poll_id" 