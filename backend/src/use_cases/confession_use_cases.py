"""
Use Cases для управления признаниями.
"""
from datetime import datetime
from typing import List, Optional

from loguru import logger

from src.entities.confession import (
    Attachment,
    Confession,
    ModerationLog,
    Poll,
    PollOption,
    PublishedRecord,
    Tag,
)
from src.entities.enums import ConfessionStatus
from src.interface_adapters.dto import ConfessionDTO, PollDTO
from src.interface_adapters.gateway_protocols import (
    ModerationGatewayProtocol,
    TelegramGatewayProtocol,
)
from src.interface_adapters.repository_protocols import ConfessionRepositoryProtocol
from src.use_cases.base import AbstractUseCase


class CreateConfessionUseCase(AbstractUseCase[ConfessionDTO, ConfessionDTO]):
    """Use Case для создания нового признания."""
    
    def __init__(self, confession_repository: ConfessionRepositoryProtocol) -> None:
        """
        Инициализация Use Case.
        
        Args:
            confession_repository: Репозиторий для работы с признаниями
        """
        self._confession_repository = confession_repository
    
    async def execute(self, confession_dto: ConfessionDTO) -> ConfessionDTO:
        """
        Создает новое признание на основе DTO.
        
        Args:
            confession_dto: DTO с данными признания
            
        Returns:
            ConfessionDTO: DTO созданного признания с присвоенным ID
        """
        logger.info(f"Creating new confession: {confession_dto.content[:50]}...")
        
        # Преобразуем DTO в доменную сущность
        confession = Confession(
            content=confession_dto.content,
            created_at=confession_dto.created_at,
            status=ConfessionStatus.PENDING,
            attachments=[
                Attachment(
                    url=attachment.url,
                    type=attachment.type,
                    uploaded_at=attachment.uploaded_at,
                    caption=attachment.caption,
                )
                for attachment in confession_dto.attachments
            ],
            tags=[Tag(name=tag.name) for tag in confession_dto.tags],
        )
        
        # Если есть опрос, добавляем его
        if confession_dto.poll:
            confession.poll = Poll(
                question=confession_dto.poll.question,
                allows_multiple_answers=confession_dto.poll.allows_multiple_answers,
                type=confession_dto.poll.type,
                correct_option_id=confession_dto.poll.correct_option_id,
                explanation=confession_dto.poll.explanation,
                open_period=confession_dto.poll.open_period,
                options=[
                    PollOption(text=option.text, vote_count=option.vote_count)
                    for option in confession_dto.poll.options
                ],
            )
        
        # Сохраняем в репозитории
        saved_confession = await self._confession_repository.save(confession)
        
        # Преобразуем обратно в DTO и возвращаем
        return ConfessionDTO.model_validate(saved_confession, from_attributes=True)


class ModerateConfessionUseCase(AbstractUseCase[ConfessionDTO, bool]):
    """Use Case для модерации признания."""
    
    def __init__(
        self,
        moderation_gateway: ModerationGatewayProtocol,
        confession_repository: ConfessionRepositoryProtocol,
    ) -> None:
        """
        Инициализация Use Case.
        
        Args:
            moderation_gateway: Гейтвей для работы с системой модерации
            confession_repository: Репозиторий для работы с признаниями
        """
        self._moderation_gateway = moderation_gateway
        self._confession_repository = confession_repository
    
    async def execute(self, confession_dto: ConfessionDTO) -> bool:
        """
        Проводит модерацию признания.
        
        Args:
            confession_dto: DTO с данными признания
            
        Returns:
            bool: True, если признание одобрено, False - если отклонено
        """
        logger.info(f"Moderating confession ID {confession_dto.id}")
        
        # Получаем признание из репозитория
        confession = await self._confession_repository.get_by_id(confession_dto.id)
        if not confession:
            logger.error(f"Confession with ID {confession_dto.id} not found")
            return False
        
        # Отправляем на модерацию
        moderation_status = await self._moderation_gateway.moderate(confession)
        
        # Получаем причину отклонения, если есть
        moderation_reason = None
        if moderation_status == ConfessionStatus.REJECTED:
            moderation_reason = await self._moderation_gateway.get_moderation_reason(confession)
            logger.info(f"Confession ID {confession_dto.id} rejected: {moderation_reason}")
        
        # Создаем запись о модерации
        moderation_log = ModerationLog(
            confession_id=confession.id,
            decision=moderation_status,
            moderator="LLM",  # В будущем можно передавать имя модератора
            reason=moderation_reason,
            timestamp=datetime.now(),
        )
        
        # Обновляем статус признания
        confession.status = moderation_status
        confession.moderation_logs.append(moderation_log)
        
        # Сохраняем изменения
        await self._confession_repository.save(confession)
        
        # Возвращаем результат модерации
        return moderation_status == ConfessionStatus.APPROVED


class PublishConfessionUseCase(AbstractUseCase[ConfessionDTO, ConfessionDTO]):
    """Use Case для публикации признания в Telegram."""
    
    def __init__(
        self,
        telegram_gateway: TelegramGatewayProtocol,
        confession_repository: ConfessionRepositoryProtocol,
    ) -> None:
        """
        Инициализация Use Case.
        
        Args:
            telegram_gateway: Гейтвей для работы с Telegram
            confession_repository: Репозиторий для работы с признаниями
        """
        self._telegram_gateway = telegram_gateway
        self._confession_repository = confession_repository
    
    async def execute(self, confession_dto: ConfessionDTO) -> ConfessionDTO:
        """
        Публикует признание в Telegram.
        
        Args:
            confession_dto: DTO с данными признания
            
        Returns:
            ConfessionDTO: DTO опубликованного признания
        """
        logger.info(f"Publishing confession ID {confession_dto.id}")
        
        # Получаем признание из репозитория
        confession = await self._confession_repository.get_by_id(confession_dto.id)
        if not confession:
            logger.error(f"Confession with ID {confession_dto.id} not found")
            raise ValueError(f"Confession with ID {confession_dto.id} not found")
        
        # Проверяем, что признание одобрено
        if confession.status != ConfessionStatus.APPROVED:
            logger.error(f"Cannot publish confession with status {confession.status}")
            raise ValueError(f"Cannot publish confession with status {confession.status}")
        
        # Отправляем признание в Telegram
        message_id = await self._telegram_gateway.send_confession(confession)
        
        # Если есть опрос, отправляем его
        poll_message_id = None
        if confession.poll:
            poll_message_id = await self._telegram_gateway.send_poll(confession.poll)
            confession.poll.poll_message_id = poll_message_id
        
        # Создаем запись о публикации
        published_record = PublishedRecord(
            confession_id=confession.id,
            telegram_message_id=message_id,
            channel_id="@falt_conf",  # В будущем можно передавать ID канала
            published_at=datetime.now(),
        )
        
        # Обновляем статус признания
        confession.status = ConfessionStatus.PUBLISHED
        confession.published_record = published_record
        
        # Сохраняем изменения
        updated_confession = await self._confession_repository.save(confession)
        
        # Преобразуем обратно в DTO и возвращаем
        return ConfessionDTO.model_validate(updated_confession, from_attributes=True) 