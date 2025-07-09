"""
Тесты для CreateConfessionUseCase.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.entities.confession import Confession
from src.entities.enums import ConfessionStatus
from src.interface_adapters.dto import ConfessionDTO, AttachmentDTO, TagDTO, PollDTO, PollOptionDTO
from src.use_cases.confession_use_cases import CreateConfessionUseCase


class TestCreateConfessionUseCase:
    """Тесты для CreateConfessionUseCase."""
    
    @pytest.fixture
    def confession_repository_mock(self):
        """Создает мок репозитория признаний."""
        repository = AsyncMock()
        
        # Настраиваем метод save
        async def save_mock(confession):
            # Симулируем сохранение, устанавливая ID
            confession.id = 1
            return confession
        
        repository.save.side_effect = save_mock
        return repository
    
    @pytest.fixture
    def confession_dto(self):
        """Создает DTO для тестирования."""
        return ConfessionDTO(
            content="Тестовое признание",
            attachments=[
                AttachmentDTO(
                    url="https://example.com/image.jpg",
                    type="IMAGE",
                ),
            ],
            tags=[
                TagDTO(name="тест"),
                TagDTO(name="пример"),
            ],
        )
    
    @pytest.mark.asyncio
    async def test_execute_creates_confession(self, confession_repository_mock, confession_dto):
        """Тест создания признания."""
        # Arrange
        use_case = CreateConfessionUseCase(confession_repository_mock)
        
        # Act
        result = await use_case.execute(confession_dto)
        
        # Assert
        # Проверяем, что метод save вызван
        confession_repository_mock.save.assert_called_once()
        
        # Проверяем результат
        assert result.id == 1
        assert result.content == confession_dto.content
        assert result.status == ConfessionStatus.PENDING
        assert len(result.attachments) == 1
        assert len(result.tags) == 2
    
    @pytest.mark.asyncio
    async def test_execute_with_poll(self, confession_repository_mock):
        """Тест создания признания с опросом."""
        # Arrange
        confession_dto = ConfessionDTO(
            content="Признание с опросом",
            poll=PollDTO(
                question="Тестовый вопрос",
                options=[
                    PollOptionDTO(text="Вариант 1"),
                    PollOptionDTO(text="Вариант 2"),
                ],
                allows_multiple_answers=True,
            ),
        )
        
        use_case = CreateConfessionUseCase(confession_repository_mock)
        
        # Act
        result = await use_case.execute(confession_dto)
        
        # Assert
        confession_repository_mock.save.assert_called_once()
        
        assert result.id == 1
        assert result.content == confession_dto.content
        assert result.poll is not None
        assert result.poll.question == confession_dto.poll.question
        assert len(result.poll.options) == 2
        assert result.poll.allows_multiple_answers is True 