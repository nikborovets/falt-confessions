"""
SQLAlchemy-реализация репозитория для признаний.
"""
from typing import List, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.entities.confession import (
    Attachment,
    Comment,
    Confession,
    ModerationLog,
    Poll,
    PollOption,
    PublishedRecord,
    Tag,
)
from src.entities.enums import ConfessionStatus
from src.frameworks_and_drivers.models.confession import (
    AttachmentModel,
    CommentModel,
    ConfessionModel,
    ModerationLogModel,
    PollModel,
    PollOptionModel,
    PublishedRecordModel,
    TagModel,
)
from src.interface_adapters.repository_protocols import ConfessionRepositoryProtocol


class SqlAlchemyConfessionRepository(ConfessionRepositoryProtocol):
    """SQLAlchemy-реализация репозитория для признаний."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация репозитория.
        
        Args:
            session: Активная сессия SQLAlchemy
        """
        self._session = session
    
    async def save(self, confession: Confession) -> Confession:
        """
        Сохраняет признание в базе данных.
        
        Args:
            confession: Доменная сущность признания
            
        Returns:
            Confession: Сохраненное признание с обновленными ID
        """
        # Проверяем, существует ли уже признание с таким ID
        if confession.id:
            # Обновляем существующее признание
            stmt = select(ConfessionModel).where(ConfessionModel.id == confession.id)
            result = await self._session.execute(stmt)
            confession_model = result.scalars().first()
            
            if not confession_model:
                logger.warning(f"Confession with ID {confession.id} not found, creating new")
                confession_model = ConfessionModel()
        else:
            # Создаем новое признание
            confession_model = ConfessionModel()
        
        # Обновляем основные поля
        confession_model.content = confession.content
        confession_model.status = confession.status
        confession_model.created_at = confession.created_at
        
        # Сохраняем модель в БД для получения ID
        self._session.add(confession_model)
        await self._session.flush()
        
        # Обновляем ID в доменной сущности
        confession.id = confession_model.id
        
        # Обрабатываем вложения
        if confession.attachments:
            # Удаляем старые вложения, если это обновление
            if confession_model.attachments:
                for attachment_model in confession_model.attachments:
                    await self._session.delete(attachment_model)
                await self._session.flush()
            
            # Добавляем новые вложения
            for attachment in confession.attachments:
                attachment_model = AttachmentModel(
                    confession_id=confession_model.id,
                    url=attachment.url,
                    type=attachment.type,
                    uploaded_at=attachment.uploaded_at,
                    caption=attachment.caption,
                )
                self._session.add(attachment_model)
        
        # Обрабатываем теги
        if confession.tags:
            # Очищаем старые связи тегов
            confession_model.tags = []
            await self._session.flush()
            
            # Добавляем новые теги
            for tag in confession.tags:
                # Ищем существующий тег или создаем новый
                stmt = select(TagModel).where(TagModel.name == tag.name)
                result = await self._session.execute(stmt)
                tag_model = result.scalars().first()
                
                if not tag_model:
                    tag_model = TagModel(name=tag.name)
                    self._session.add(tag_model)
                    await self._session.flush()
                    
                # Связываем тег с признанием
                confession_model.tags.append(tag_model)
        
        # Обрабатываем опрос, если он есть
        if confession.poll:
            # Если есть существующий опрос, удаляем его
            if confession_model.poll:
                await self._session.delete(confession_model.poll)
                await self._session.flush()
            
            # Создаем новый опрос
            poll_model = PollModel(
                confession_id=confession_model.id,
                question=confession.poll.question,
                allows_multiple_answers=confession.poll.allows_multiple_answers,
                type=confession.poll.type,
                correct_option_id=confession.poll.correct_option_id,
                explanation=confession.poll.explanation,
                open_period=confession.poll.open_period,
                poll_message_id=confession.poll.poll_message_id,
                created_at=confession.poll.created_at,
            )
            self._session.add(poll_model)
            await self._session.flush()
            
            # Добавляем варианты опроса
            for option in confession.poll.options:
                option_model = PollOptionModel(
                    poll_id=poll_model.id,
                    text=option.text,
                    vote_count=option.vote_count,
                )
                self._session.add(option_model)
        
        # Обрабатываем записи о модерации
        if confession.moderation_logs:
            # Добавляем только новые записи
            for log in confession.moderation_logs:
                if not log.id:  # Новая запись
                    log_model = ModerationLogModel(
                        confession_id=confession_model.id,
                        decision=log.decision,
                        moderator=log.moderator,
                        reason=log.reason,
                        timestamp=log.timestamp,
                    )
                    self._session.add(log_model)
        
        # Обрабатываем запись о публикации
        if confession.published_record:
            # Если есть существующая запись, удаляем её
            if confession_model.published_record:
                await self._session.delete(confession_model.published_record)
                await self._session.flush()
            
            # Создаем новую запись
            published_record_model = PublishedRecordModel(
                confession_id=confession_model.id,
                telegram_message_id=confession.published_record.telegram_message_id,
                channel_id=confession.published_record.channel_id,
                published_at=confession.published_record.published_at,
                discussion_thread_id=confession.published_record.discussion_thread_id,
            )
            self._session.add(published_record_model)
        
        # Применяем все изменения
        await self._session.commit()
        
        # Возвращаем обновленную доменную сущность
        return await self.get_by_id(confession_model.id)
    
    async def get_by_id(self, id: int) -> Optional[Confession]:
        """
        Получает признание по ID.
        
        Args:
            id: ID признания
            
        Returns:
            Optional[Confession]: Найденное признание или None
        """
        # Формируем запрос с предзагрузкой связанных сущностей
        stmt = (
            select(ConfessionModel)
            .where(ConfessionModel.id == id)
            .options(
                selectinload(ConfessionModel.attachments),
                selectinload(ConfessionModel.tags),
                selectinload(ConfessionModel.poll).selectinload(PollModel.options),
                selectinload(ConfessionModel.moderation_logs),
                selectinload(ConfessionModel.published_record),
                selectinload(ConfessionModel.comments),
            )
        )
        
        result = await self._session.execute(stmt)
        confession_model = result.scalars().first()
        
        if not confession_model:
            return None
        
        # Преобразуем в доменную сущность
        return self._map_to_domain(confession_model)
    
    async def list_by_status(self, status: ConfessionStatus) -> List[Confession]:
        """
        Получает список признаний по статусу.
        
        Args:
            status: Статус признаний
            
        Returns:
            List[Confession]: Список признаний
        """
        # Формируем запрос с предзагрузкой связанных сущностей
        stmt = (
            select(ConfessionModel)
            .where(ConfessionModel.status == status)
            .options(
                selectinload(ConfessionModel.attachments),
                selectinload(ConfessionModel.tags),
                selectinload(ConfessionModel.poll).selectinload(PollModel.options),
                selectinload(ConfessionModel.moderation_logs),
                selectinload(ConfessionModel.published_record),
                selectinload(ConfessionModel.comments),
            )
        )
        
        result = await self._session.execute(stmt)
        confession_models = result.scalars().all()
        
        # Преобразуем каждую модель в доменную сущность
        return [self._map_to_domain(model) for model in confession_models]
    
    async def update_status(self, id: int, status: ConfessionStatus) -> None:
        """
        Обновляет статус признания.
        
        Args:
            id: ID признания
            status: Новый статус
        """
        # Находим признание по ID
        stmt = select(ConfessionModel).where(ConfessionModel.id == id)
        result = await self._session.execute(stmt)
        confession_model = result.scalars().first()
        
        if not confession_model:
            logger.error(f"Confession with ID {id} not found")
            return
        
        # Обновляем статус
        confession_model.status = status
        
        # Сохраняем изменения
        await self._session.commit()
    
    def _map_to_domain(self, model: ConfessionModel) -> Confession:
        """
        Преобразует ORM-модель в доменную сущность.
        
        Args:
            model: ORM-модель признания
            
        Returns:
            Confession: Доменная сущность
        """
        # Преобразуем вложения
        attachments = [
            Attachment(
                id=attachment.id,
                url=attachment.url,
                type=attachment.type,
                uploaded_at=attachment.uploaded_at,
                caption=attachment.caption,
            )
            for attachment in model.attachments
        ]
        
        # Преобразуем теги
        tags = [Tag(id=tag.id, name=tag.name) for tag in model.tags]
        
        # Преобразуем опрос, если есть
        poll = None
        if model.poll:
            poll_options = [
                PollOption(
                    id=option.id,
                    text=option.text,
                    vote_count=option.vote_count,
                )
                for option in model.poll.options
            ]
            
            poll = Poll(
                id=model.poll.id,
                question=model.poll.question,
                allows_multiple_answers=model.poll.allows_multiple_answers,
                type=model.poll.type,
                correct_option_id=model.poll.correct_option_id,
                explanation=model.poll.explanation,
                open_period=model.poll.open_period,
                poll_message_id=model.poll.poll_message_id,
                created_at=model.poll.created_at,
                options=poll_options,
            )
        
        # Преобразуем модерационные записи
        moderation_logs = [
            ModerationLog(
                id=log.id,
                confession_id=log.confession_id,
                decision=log.decision,
                moderator=log.moderator,
                reason=log.reason,
                timestamp=log.timestamp,
            )
            for log in model.moderation_logs
        ]
        
        # Преобразуем запись о публикации, если есть
        published_record = None
        if model.published_record:
            published_record = PublishedRecord(
                id=model.published_record.id,
                confession_id=model.published_record.confession_id,
                telegram_message_id=model.published_record.telegram_message_id,
                channel_id=model.published_record.channel_id,
                published_at=model.published_record.published_at,
                discussion_thread_id=model.published_record.discussion_thread_id,
            )
        
        # Преобразуем комментарии
        comments = [
            Comment(
                id=comment.id,
                confession_id=comment.confession_id,
                content=comment.content,
                created_at=comment.created_at,
                reply_to=comment.reply_to,
            )
            for comment in model.comments
        ]
        
        # Создаем доменную сущность
        return Confession(
            id=model.id,
            content=model.content,
            created_at=model.created_at,
            status=model.status,
            attachments=attachments,
            tags=tags,
            poll=poll,
            moderation_logs=moderation_logs,
            published_record=published_record,
            comments=comments,
        ) 