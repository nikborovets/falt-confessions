"""
Тесты для PublishConfessionUseCase.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.entities.confession import Confession, Poll, PollOption
from src.entities.enums import ConfessionStatus
from src.interface_adapters.dto import ConfessionDTO
from src.use_cases.confession_use_cases import PublishConfessionUseCase


class TestPublishConfessionUseCase:
    """Тесты для PublishConfessionUseCase."""
    
    @pytest.fixture
    def confession_repository_mock(self):
        """Создает мок репозитория признаний."""
        repository = AsyncMock()
        
        # Настраиваем метод get_by_id для обычного признания
        async def get_by_id_mock(id):
            # Возвращаем тестовое признание
            return Confession(
                id=id,
                content="Тестовое признание для публикации",
                status=ConfessionStatus.APPROVED,
            )
        
        repository.get_by_id.side_effect = get_by_id_mock
        repository.save.side_effect = lambda confession: confession
        return repository
    
    @pytest.fixture
    def telegram_gateway_mock(self):
        """Создает мок гейтвея Telegram."""
        gateway = AsyncMock()
        
        # Настраиваем методы
        gateway.send_confession.return_value = "message_123"
        gateway.send_poll.return_value = "poll_456"
        
        return gateway
    
    @pytest.mark.asyncio
    async def test_execute_publishes_confession(self, confession_repository_mock, telegram_gateway_mock):
        """Тест публикации признания."""
        # Arrange
        use_case = PublishConfessionUseCase(
            telegram_gateway=telegram_gateway_mock,
            confession_repository=confession_repository_mock,
        )
        
        confession_dto = ConfessionDTO(
            id=1,
            content="Тестовое признание для публикации",
            status=ConfessionStatus.APPROVED,
        )
        
        # Act
        result = await use_case.execute(confession_dto)
        
        # Assert
        # Проверяем, что методы были вызваны
        confession_repository_mock.get_by_id.assert_called_once_with(1)
        telegram_gateway_mock.send_confession.assert_called_once()
        confession_repository_mock.save.assert_called_once()
        
        # Проверяем результат
        assert result.id == 1
        assert result.status == ConfessionStatus.PUBLISHED
    
    @pytest.mark.asyncio
    async def test_execute_publishes_confession_with_poll(self, confession_repository_mock, telegram_gateway_mock):
        """Тест публикации признания с опросом."""
        # Arrange
        # Меняем поведение мока - признание с опросом
        async def get_by_id_with_poll(id):
            poll = Poll(
                question="Тестовый вопрос",
                options=[
                    PollOption(text="Вариант 1"),
                    PollOption(text="Вариант 2"),
                ],
            )
            return Confession(
                id=id,
                content="Тестовое признание с опросом",
                status=ConfessionStatus.APPROVED,
                poll=poll,
            )
        
        confession_repository_mock.get_by_id.side_effect = get_by_id_with_poll
        
        use_case = PublishConfessionUseCase(
            telegram_gateway=telegram_gateway_mock,
            confession_repository=confession_repository_mock,
        )
        
        confession_dto = ConfessionDTO(
            id=2,
            content="Тестовое признание с опросом",
            status=ConfessionStatus.APPROVED,
        )
        
        # Act
        result = await use_case.execute(confession_dto)
        
        # Assert
        # Проверяем, что методы были вызваны
        confession_repository_mock.get_by_id.assert_called_once_with(2)
        telegram_gateway_mock.send_confession.assert_called_once()
        telegram_gateway_mock.send_poll.assert_called_once()
        confession_repository_mock.save.assert_called_once()
        
        # Проверяем результат
        assert result.id == 2
        assert result.status == ConfessionStatus.PUBLISHED
    
    @pytest.mark.asyncio
    async def test_execute_confession_not_found(self, confession_repository_mock, telegram_gateway_mock):
        """Тест случая, когда признание не найдено."""
        # Arrange
        # Меняем поведение мока - признание не найдено
        confession_repository_mock.get_by_id.side_effect = None  # Сбрасываем side_effect
        confession_repository_mock.get_by_id.return_value = None
        
        use_case = PublishConfessionUseCase(
            telegram_gateway=telegram_gateway_mock,
            confession_repository=confession_repository_mock,
        )
        
        confession_dto = ConfessionDTO(
            id=999,  # Несуществующий ID
            content="",
            status=ConfessionStatus.APPROVED,
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Confession with ID {confession_dto.id} not found"):
            await use_case.execute(confession_dto)
        
        # Проверяем, что методы были вызваны
        confession_repository_mock.get_by_id.assert_called_once_with(999)
        telegram_gateway_mock.send_confession.assert_not_called()
        
    @pytest.mark.asyncio
    async def test_execute_confession_not_approved(self, confession_repository_mock, telegram_gateway_mock):
        """Тест случая, когда признание не одобрено."""
        # Arrange
        # Меняем поведение мока - признание в статусе PENDING
        async def get_by_id_pending(id):
            return Confession(
                id=id,
                content="Тестовое признание не одобрено",
                status=ConfessionStatus.PENDING,
            )
        
        confession_repository_mock.get_by_id.side_effect = get_by_id_pending
        
        use_case = PublishConfessionUseCase(
            telegram_gateway=telegram_gateway_mock,
            confession_repository=confession_repository_mock,
        )
        
        confession_dto = ConfessionDTO(
            id=3,
            content="",
            status=ConfessionStatus.PENDING,
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Cannot publish confession with status {ConfessionStatus.PENDING}"):
            await use_case.execute(confession_dto)
        
        # Проверяем, что методы были вызваны
        confession_repository_mock.get_by_id.assert_called_once_with(3)
        telegram_gateway_mock.send_confession.assert_not_called()
        confession_repository_mock.save.assert_not_called() 