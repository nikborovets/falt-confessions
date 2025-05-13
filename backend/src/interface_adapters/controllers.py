"""
Контроллеры для управления бизнес-процессами.
"""
from typing import List, Optional

from src.interface_adapters.dto import ConfessionDTO, PollDTO
from src.use_cases.confession_use_cases import (
    CreateConfessionUseCase,
    ModerateConfessionUseCase,
    PublishConfessionUseCase,
)


class ConfessionController:
    """Контроллер для управления признаниями."""
    
    def __init__(
        self,
        create_confession_use_case: CreateConfessionUseCase,
        moderate_confession_use_case: ModerateConfessionUseCase,
        publish_confession_use_case: PublishConfessionUseCase,
    ) -> None:
        """Инициализация контроллера с нужными Use Cases."""
        self._create_confession_use_case = create_confession_use_case
        self._moderate_confession_use_case = moderate_confession_use_case
        self._publish_confession_use_case = publish_confession_use_case
    
    async def create_confession(self, dto: ConfessionDTO) -> ConfessionDTO:
        """Создает новое признание."""
        return await self._create_confession_use_case.execute(dto)
    
    async def moderate_confession(self, dto: ConfessionDTO) -> bool:
        """
        Проводит модерацию признания.
        
        Returns:
            bool: True, если признание одобрено, False - если отклонено
        """
        return await self._moderate_confession_use_case.execute(dto)
    
    async def publish_confession(self, dto: ConfessionDTO) -> ConfessionDTO:
        """Публикует признание в Telegram."""
        return await self._publish_confession_use_case.execute(dto)


class PollController:
    """Контроллер для управления опросами."""
    
    def __init__(
        self,
        create_confession_use_case: CreateConfessionUseCase,
    ) -> None:
        """Инициализация контроллера с нужными Use Cases."""
        self._create_confession_use_case = create_confession_use_case
    
    async def create_poll(self, dto: PollDTO) -> PollDTO:
        """Создает новый опрос в рамках признания."""
        confession_dto = ConfessionDTO(
            content="",  # Будет заполнено позже
            poll=dto,
        )
        result = await self._create_confession_use_case.execute(confession_dto)
        return result.poll 