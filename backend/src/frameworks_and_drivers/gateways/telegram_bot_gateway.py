"""
Гейтвей для работы с Telegram-ботом.
"""
import os
from typing import Optional

import aiogram
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from loguru import logger

from src.entities.confession import Confession, Poll
from src.interface_adapters.gateway_protocols import TelegramGatewayProtocol


class TelegramBotGateway(TelegramGatewayProtocol):
    """Реализация гейтвея для работы с Telegram-ботом."""
    
    def __init__(self) -> None:
        """Инициализация бота и диспетчера."""
        # Получаем токен бота из переменных окружения
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.warning("TELEGRAM_BOT_TOKEN not set, using mock implementation")
            self._bot = None
            self._channel_id = None
        else:
            self._bot = Bot(token=token)
            self._channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "@falt_conf")
    
    async def send_confession(self, confession: Confession) -> str:
        """
        Отправляет признание в Telegram-канал.
        
        Args:
            confession: Доменная сущность признания
            
        Returns:
            str: ID сообщения в Telegram
        """
        if not self._bot:
            # Mock-реализация для тестирования
            logger.info(f"Mock: Sending confession to Telegram: {confession.content[:50]}...")
            return "mock_message_id"
        
        # Формируем текст сообщения
        message_text = f"#{confession.id}\n\n{confession.content}"
        
        # Добавляем теги, если есть
        if confession.tags:
            tags_text = " ".join([f"#{tag.name}" for tag in confession.tags])
            message_text += f"\n\n{tags_text}"
        
        try:
            # Отправляем текст признания
            message = await self._bot.send_message(
                chat_id=self._channel_id,
                text=message_text,
                parse_mode=ParseMode.HTML,
            )
            
            # Если есть вложения, отправляем их
            if confession.attachments:
                # В реальном приложении здесь будет логика отправки медиа
                # В зависимости от типа вложения (фото, видео и т.д.)
                logger.info(f"Attachments found, but not implemented yet")
            
            logger.info(f"Confession {confession.id} sent to Telegram with message_id {message.message_id}")
            return str(message.message_id)
        except Exception as e:
            logger.error(f"Error sending confession to Telegram: {str(e)}")
            raise
    
    async def send_poll(self, poll: Poll) -> str:
        """
        Отправляет опрос в Telegram-канал.
        
        Args:
            poll: Доменная сущность опроса
            
        Returns:
            str: ID сообщения с опросом в Telegram
        """
        if not self._bot:
            # Mock-реализация для тестирования
            logger.info(f"Mock: Sending poll to Telegram: {poll.question}")
            return "mock_poll_id"
        
        try:
            # Получаем варианты ответов
            options = [option.text for option in poll.options]
            
            # Отправляем опрос
            message = await self._bot.send_poll(
                chat_id=self._channel_id,
                question=poll.question,
                options=options,
                is_anonymous=True,
                allows_multiple_answers=poll.allows_multiple_answers,
                type=poll.type,
                correct_option_id=poll.correct_option_id,
                explanation=poll.explanation,
                open_period=poll.open_period,
            )
            
            logger.info(f"Poll sent to Telegram with message_id {message.message_id}")
            return str(message.message_id)
        except Exception as e:
            logger.error(f"Error sending poll to Telegram: {str(e)}")
            raise 