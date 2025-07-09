"""
Зависимости для FastAPI.
"""
from typing import Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.frameworks_and_drivers.db.database import get_db
from src.frameworks_and_drivers.gateways.llm_moderation_gateway import LLMModerationGateway
from src.frameworks_and_drivers.gateways.telegram_bot_gateway import TelegramBotGateway
from src.frameworks_and_drivers.repositories.sqlalchemy_confession_repository import (
    SqlAlchemyConfessionRepository,
)
from src.interface_adapters.controllers import ConfessionController, PollController
from src.use_cases.confession_use_cases import (
    CreateConfessionUseCase,
    ModerateConfessionUseCase,
    PublishConfessionUseCase,
)


async def get_confession_repository(
    session: AsyncSession = Depends(get_db),
) -> SqlAlchemyConfessionRepository:
    """
    Возвращает репозиторий для работы с признаниями.
    """
    return SqlAlchemyConfessionRepository(session)


async def get_telegram_gateway() -> TelegramBotGateway:
    """
    Возвращает гейтвей для работы с Telegram.
    """
    return TelegramBotGateway()


async def get_moderation_gateway() -> LLMModerationGateway:
    """
    Возвращает гейтвей для работы с системой модерации.
    """
    return LLMModerationGateway()


async def get_create_confession_use_case(
    confession_repository: SqlAlchemyConfessionRepository = Depends(get_confession_repository),
) -> CreateConfessionUseCase:
    """
    Возвращает UseCase для создания признания.
    """
    return CreateConfessionUseCase(confession_repository)


async def get_moderate_confession_use_case(
    moderation_gateway: LLMModerationGateway = Depends(get_moderation_gateway),
    confession_repository: SqlAlchemyConfessionRepository = Depends(get_confession_repository),
) -> ModerateConfessionUseCase:
    """
    Возвращает UseCase для модерации признания.
    """
    return ModerateConfessionUseCase(moderation_gateway, confession_repository)


async def get_publish_confession_use_case(
    telegram_gateway: TelegramBotGateway = Depends(get_telegram_gateway),
    confession_repository: SqlAlchemyConfessionRepository = Depends(get_confession_repository),
) -> PublishConfessionUseCase:
    """
    Возвращает UseCase для публикации признания.
    """
    return PublishConfessionUseCase(telegram_gateway, confession_repository)


async def get_confession_controller(
    create_confession_use_case: CreateConfessionUseCase = Depends(get_create_confession_use_case),
    moderate_confession_use_case: ModerateConfessionUseCase = Depends(get_moderate_confession_use_case),
    publish_confession_use_case: PublishConfessionUseCase = Depends(get_publish_confession_use_case),
) -> ConfessionController:
    """
    Возвращает контроллер для работы с признаниями.
    """
    return ConfessionController(
        create_confession_use_case,
        moderate_confession_use_case,
        publish_confession_use_case,
    )


async def get_poll_controller(
    create_confession_use_case: CreateConfessionUseCase = Depends(get_create_confession_use_case),
) -> PollController:
    """
    Возвращает контроллер для работы с опросами.
    """
    return PollController(create_confession_use_case) 