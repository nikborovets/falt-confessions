"""
Тесты для ModerateConfessionUseCase.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.entities.confession import Confession
from src.entities.enums import ConfessionStatus
from src.interface_adapters.dto import ConfessionDTO
from src.use_cases.confession_use_cases import ModerateConfessionUseCase


class TestModerateConfessionUseCase:
    """Тесты для ModerateConfessionUseCase."""
    
    @pytest.fixture
    def confession_repository_mock(self):
        """Создает мок репозитория признаний."""
        repository = AsyncMock()
        
        # Настраиваем метод get_by_id
        async def get_by_id_mock(id):
            # Возвращаем тестовое признание
            return Confession(
                id=id,
                content="Тестовое признание для модерации",
                status=ConfessionStatus.PENDING,
            )
        
        repository.get_by_id.side_effect = get_by_id_mock
        repository.save.side_effect = lambda confession: confession
        return repository
    
    @pytest.fixture
    def moderation_gateway_mock(self):
        """Создает мок гейтвея модерации."""
        gateway = AsyncMock()
        
        # Можем указать разные результаты для разных тестов
        gateway.moderate.return_value = ConfessionStatus.APPROVED
        gateway.get_moderation_reason.return_value = None
        
        return gateway
    
    @pytest.mark.asyncio
    async def test_execute_approves_confession(self, confession_repository_mock, moderation_gateway_mock):
        """Тест одобрения признания."""
        # Arrange
        use_case = ModerateConfessionUseCase(
            moderation_gateway=moderation_gateway_mock,
            confession_repository=confession_repository_mock,
        )
        
        confession_dto = ConfessionDTO(
            id=1,
            content="Тестовое признание для модерации",
            status=ConfessionStatus.PENDING,
        )
        
        # Act
        result = await use_case.execute(confession_dto)
        
        # Assert
        # Проверяем, что метод moderate был вызван
        moderation_gateway_mock.moderate.assert_called_once()
        
        # Проверяем, что признание было сохранено
        confession_repository_mock.save.assert_called_once()
        
        # Проверяем результат
        assert result is True
    
    @pytest.mark.asyncio
    async def test_execute_rejects_confession(self, confession_repository_mock, moderation_gateway_mock):
        """Тест отклонения признания."""
        # Arrange
        # Меняем поведение мока для этого теста
        moderation_gateway_mock.moderate.return_value = ConfessionStatus.REJECTED
        moderation_gateway_mock.get_moderation_reason.return_value = "Содержание нарушает правила"
        
        use_case = ModerateConfessionUseCase(
            moderation_gateway=moderation_gateway_mock,
            confession_repository=confession_repository_mock,
        )
        
        confession_dto = ConfessionDTO(
            id=1,
            content="Тестовое признание для модерации",
            status=ConfessionStatus.PENDING,
        )
        
        # Act
        result = await use_case.execute(confession_dto)
        
        # Assert
        # Проверяем, что метод moderate был вызван
        moderation_gateway_mock.moderate.assert_called_once()
        
        # Проверяем, что была запрошена причина отклонения
        moderation_gateway_mock.get_moderation_reason.assert_called_once()
        
        # Проверяем, что признание было сохранено
        confession_repository_mock.save.assert_called_once()
        
        # Проверяем результат
        assert result is False
    
    @pytest.mark.asyncio
    async def test_execute_confession_not_found(self, confession_repository_mock, moderation_gateway_mock):
        """Тест случая, когда признание не найдено."""
        # Arrange
        # Сбрасываем предыдущие настройки мока и устанавливаем новые
        confession_repository_mock.get_by_id.side_effect = None
        confession_repository_mock.get_by_id.return_value = None
        
        use_case = ModerateConfessionUseCase(
            moderation_gateway=moderation_gateway_mock,
            confession_repository=confession_repository_mock,
        )
        
        confession_dto = ConfessionDTO(
            id=999,  # Несуществующий ID
            content="",
            status=ConfessionStatus.PENDING,
        )
        
        # Act
        result = await use_case.execute(confession_dto)
        
        # Assert
        # Проверяем, что метод get_by_id был вызван
        confession_repository_mock.get_by_id.assert_called_once_with(999)
        
        # Проверяем результат
        assert result is False 