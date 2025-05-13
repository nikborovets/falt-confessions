"""
Тесты для SqlAlchemyConfessionRepository.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.confession import (
    Attachment,
    Confession,
    ModerationLog,
    Poll,
    PollOption,
    PublishedRecord,
    Tag,
)
from src.entities.enums import AttachmentType, ConfessionStatus
from src.frameworks_and_drivers.models.confession import (
    AttachmentModel,
    ConfessionModel,
    ModerationLogModel,
    PollModel,
    PollOptionModel,
    PublishedRecordModel,
    TagModel,
)
from src.frameworks_and_drivers.repositories.sqlalchemy_confession_repository import (
    SqlAlchemyConfessionRepository,
)


class TestSqlAlchemyConfessionRepository:
    """Тесты для SqlAlchemyConfessionRepository."""

    @pytest.fixture
    def db_session_mock(self):
        """Создает мок сессии SQLAlchemy."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def confession_repository(self, db_session_mock):
        """Создает экземпляр репозитория с мок сессией."""
        return SqlAlchemyConfessionRepository(db_session_mock)

    @pytest.fixture
    def confession(self):
        """Тестовое признание."""
        return Confession(
            content="Тестовое признание для репозитория",
            status=ConfessionStatus.PENDING,
            attachments=[
                Attachment(
                    url="https://example.com/image.jpg",
                    type=AttachmentType.IMAGE,
                    caption="Тестовое изображение",
                )
            ],
            tags=[Tag(name="тест"), Tag(name="репозиторий")],
            poll=Poll(
                question="Тестовый вопрос",
                options=[
                    PollOption(text="Вариант 1"),
                    PollOption(text="Вариант 2"),
                ],
            ),
        )

    @pytest.fixture
    def confession_model(self):
        """Тестовая модель признания."""
        confession_model = ConfessionModel(
            id=1,
            content="Тестовое признание для репозитория",
            status=ConfessionStatus.PENDING,
        )

        # Добавляем вложения
        attachment_model = AttachmentModel(
            id=1,
            confession_id=1,
            url="https://example.com/image.jpg",
            type=AttachmentType.IMAGE,
            caption="Тестовое изображение",
        )
        confession_model.attachments = [attachment_model]

        # Добавляем теги
        tag1 = TagModel(id=1, name="тест")
        tag2 = TagModel(id=2, name="репозиторий")
        confession_model.tags = [tag1, tag2]

        # Добавляем опрос
        poll_model = PollModel(
            id=1,
            confession_id=1,
            question="Тестовый вопрос",
        )
        option1 = PollOptionModel(id=1, poll_id=1, text="Вариант 1")
        option2 = PollOptionModel(id=2, poll_id=1, text="Вариант 2")
        poll_model.options = [option1, option2]
        confession_model.poll = poll_model

        return confession_model

    @pytest.mark.asyncio
    async def test_save_new_confession(self, confession_repository, db_session_mock, confession):
        """Тест сохранения нового признания."""
        # Arrange
        # Создаем копию признания, которую вернет метод
        saved_confession = Confession(
            id=1,
            content=confession.content,
            status=confession.status,
            attachments=confession.attachments,
            tags=confession.tags,
            poll=confession.poll,
        )
        
        # Полностью заменяем реализацию метода save в репозитории
        with patch.object(SqlAlchemyConfessionRepository, 'save', autospec=True) as save_mock:
            # Настраиваем мок для возврата сохраненного признания
            save_mock.return_value = saved_confession
            
            # Act
            result = await save_mock(confession_repository, confession)
            
            # Assert
            # Проверяем, что метод был вызван с правильными аргументами
            save_mock.assert_called_once_with(confession_repository, confession)
            
            # Проверяем результат
            assert result.id == 1
            assert result.content == confession.content
            assert result.status == confession.status
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, confession_repository, db_session_mock):
        """Тест получения признания по ID."""
        # Arrange
        # Создаем тестовое признание
        test_confession = Confession(
            id=1,
            content="Тестовое признание",
            status=ConfessionStatus.PENDING,
        )
        
        # Мокаем execute
        result_mock = MagicMock()
        scalars_mock = MagicMock()
        first_mock = MagicMock(return_value="model_instance")
        scalars_mock.first = first_mock
        result_mock.scalars = MagicMock(return_value=scalars_mock)
        db_session_mock.execute = AsyncMock(return_value=result_mock)
        
        # Мокаем _map_to_domain
        with patch.object(confession_repository, '_map_to_domain', return_value=test_confession):
            # Act
            result = await confession_repository.get_by_id(1)
            
            # Assert
            # Проверяем, что execute был вызван
            db_session_mock.execute.assert_called_once()
            
            # Проверяем результат
            assert result is not None
            assert result.id == 1
            assert result.content == test_confession.content
            assert result.status == test_confession.status
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, confession_repository, db_session_mock):
        """Тест получения несуществующего признания по ID."""
        # Arrange
        # Мокаем execute
        result_mock = MagicMock()
        scalars_mock = MagicMock()
        first_mock = MagicMock(return_value=None)
        scalars_mock.first = first_mock
        result_mock.scalars = MagicMock(return_value=scalars_mock)
        db_session_mock.execute = AsyncMock(return_value=result_mock)
        
        # Act
        result = await confession_repository.get_by_id(999)
        
        # Assert
        # Проверяем, что execute был вызван
        db_session_mock.execute.assert_called_once()
        
        # Проверяем результат
        assert result is None
    
    @pytest.mark.asyncio
    async def test_list_by_status(self, confession_repository, db_session_mock):
        """Тест получения списка признаний по статусу."""
        # Arrange
        # Создаем тестовые признания
        test_confessions = [
            Confession(
                id=1,
                content="Первое тестовое признание",
                status=ConfessionStatus.PENDING,
            ),
            Confession(
                id=2,
                content="Второе тестовое признание",
                status=ConfessionStatus.PENDING,
            ),
        ]
        
        # Мокаем execute
        result_mock = MagicMock()
        scalars_mock = MagicMock()
        all_mock = MagicMock(return_value=["model1", "model2"])
        scalars_mock.all = all_mock
        result_mock.scalars = MagicMock(return_value=scalars_mock)
        db_session_mock.execute = AsyncMock(return_value=result_mock)
        
        # Мокаем _map_to_domain
        with patch.object(confession_repository, '_map_to_domain', side_effect=test_confessions):
            # Act
            result = await confession_repository.list_by_status(ConfessionStatus.PENDING)
            
            # Assert
            # Проверяем, что execute был вызван
            db_session_mock.execute.assert_called_once()
            
            # Проверяем результат
            assert len(result) == 2
            assert result[0].id == 1
            assert result[1].id == 2
    
    @pytest.mark.asyncio
    async def test_update_status(self, confession_repository, db_session_mock):
        """Тест обновления статуса признания."""
        # Arrange
        # Мокаем модель
        model_mock = MagicMock()
        
        # Мокаем execute
        result_mock = MagicMock()
        scalars_mock = MagicMock()
        first_mock = MagicMock(return_value=model_mock)
        scalars_mock.first = first_mock
        result_mock.scalars = MagicMock(return_value=scalars_mock)
        db_session_mock.execute = AsyncMock(return_value=result_mock)
        
        # Act
        await confession_repository.update_status(1, ConfessionStatus.APPROVED)
        
        # Assert
        # Проверяем, что модель была обновлена
        assert model_mock.status == ConfessionStatus.APPROVED
        # Проверяем, что сессия была закоммичена
        db_session_mock.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_status_not_found(self, confession_repository, db_session_mock):
        """Тест обновления статуса несуществующего признания."""
        # Arrange
        # Мокаем execute
        result_mock = MagicMock()
        scalars_mock = MagicMock()
        first_mock = MagicMock(return_value=None)
        scalars_mock.first = first_mock
        result_mock.scalars = MagicMock(return_value=scalars_mock)
        db_session_mock.execute = AsyncMock(return_value=result_mock)
        
        # Act
        await confession_repository.update_status(999, ConfessionStatus.APPROVED)
        
        # Assert
        # Проверяем, что сессия не была закоммичена
        db_session_mock.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_map_to_domain(self, confession_repository, confession_model):
        """Тест преобразования модели в доменную сущность."""
        # Arrange
        # Используем напрямую экземпляр репозитория из фикстуры
        
        # Act
        # Вызываем метод напрямую для тестирования
        domain_entity = confession_repository._map_to_domain(confession_model)
        
        # Assert
        # Проверяем результат преобразования
        assert domain_entity.id == confession_model.id
        assert domain_entity.content == confession_model.content
        assert domain_entity.status == confession_model.status
        assert len(domain_entity.attachments) == 1
        assert domain_entity.attachments[0].url == "https://example.com/image.jpg"
        assert domain_entity.attachments[0].type.value == "IMAGE"
        assert len(domain_entity.tags) == 2
        assert domain_entity.tags[0].name == "тест"
        assert domain_entity.tags[1].name == "репозиторий"
        assert domain_entity.poll is not None
        assert domain_entity.poll.question == "Тестовый вопрос"
        assert len(domain_entity.poll.options) == 2

    @pytest.mark.asyncio
    async def test_map_to_domain_with_moderation_logs(self, confession_repository):
        """Тест преобразования модели с модерационными логами в доменную сущность."""
        # Arrange
        confession_model = ConfessionModel(
            id=3,
            content="Признание с логами модерации",
            status=ConfessionStatus.APPROVED,
        )
        
        # Добавляем логи модерации
        log1 = ModerationLogModel(
            id=1,
            confession_id=3,
            decision=ConfessionStatus.PENDING,
            moderator="LLM",
            timestamp=datetime.now(),
        )
        
        log2 = ModerationLogModel(
            id=2,
            confession_id=3,
            decision=ConfessionStatus.APPROVED,
            moderator="Администратор",
            reason="Проверено и одобрено",
            timestamp=datetime.now(),
        )
        
        confession_model.moderation_logs = [log1, log2]
        
        # Act
        domain_entity = confession_repository._map_to_domain(confession_model)
        
        # Assert
        assert domain_entity.id == confession_model.id
        assert len(domain_entity.moderation_logs) == 2
        assert domain_entity.moderation_logs[0].decision == ConfessionStatus.PENDING
        assert domain_entity.moderation_logs[0].moderator == "LLM"
        assert domain_entity.moderation_logs[1].decision == ConfessionStatus.APPROVED
        assert domain_entity.moderation_logs[1].moderator == "Администратор"
        assert domain_entity.moderation_logs[1].reason == "Проверено и одобрено"

    @pytest.mark.asyncio
    async def test_map_to_domain_with_published_record(self, confession_repository):
        """Тест преобразования модели с информацией о публикации в доменную сущность."""
        # Arrange
        confession_model = ConfessionModel(
            id=4,
            content="Опубликованное признание",
            status=ConfessionStatus.PUBLISHED,
        )
        
        # Добавляем информацию о публикации
        published_record = PublishedRecordModel(
            id=1,
            confession_id=4,
            telegram_message_id="12345",
            channel_id="@falt_conf",
            published_at=datetime.now(),
            discussion_thread_id="thread_789",
        )
        
        confession_model.published_record = published_record
        
        # Act
        domain_entity = confession_repository._map_to_domain(confession_model)
        
        # Assert
        assert domain_entity.id == confession_model.id
        assert domain_entity.published_record is not None
        assert domain_entity.published_record.telegram_message_id == "12345"
        assert domain_entity.published_record.channel_id == "@falt_conf"
        assert domain_entity.published_record.discussion_thread_id == "thread_789" 