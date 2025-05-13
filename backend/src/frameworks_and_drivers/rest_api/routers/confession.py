"""
Роутер для работы с признаниями.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.enums import ConfessionStatus
from src.frameworks_and_drivers.db.database import get_db
from src.frameworks_and_drivers.dependencies import get_confession_controller
from src.frameworks_and_drivers.rest_api.schemas import (
    ConfessionRequest,
    ConfessionResponse,
    StatusUpdateRequest,
)
from src.interface_adapters.controllers import ConfessionController
from src.interface_adapters.dto import (
    AttachmentDTO,
    ConfessionDTO,
    PollDTO,
    PollOptionDTO,
    TagDTO,
)

router = APIRouter(prefix="/confessions", tags=["confessions"])


@router.post("/", response_model=ConfessionResponse, status_code=status.HTTP_201_CREATED)
async def post_confession(
    request: ConfessionRequest,
    confession_controller: ConfessionController = Depends(get_confession_controller),
) -> ConfessionResponse:
    """
    Создает новое признание.
    """
    logger.info(f"Creating new confession: {request.content[:50]}...")
    
    # Преобразуем запрос в DTO
    confession_dto = ConfessionDTO(
        content=request.content,
        attachments=[
            AttachmentDTO(
                url=attachment.url,
                type=attachment.type,
                caption=attachment.caption,
            )
            for attachment in request.attachments
        ],
        tags=[TagDTO(name=tag.name) for tag in request.tags],
    )
    
    # Если есть опрос, добавляем его
    if request.poll:
        confession_dto.poll = PollDTO(
            question=request.poll.question,
            options=[
                PollOptionDTO(text=option.text)
                for option in request.poll.options
            ],
            allows_multiple_answers=request.poll.allows_multiple_answers,
            type=request.poll.type,
            correct_option_id=request.poll.correct_option_id,
            explanation=request.poll.explanation,
            open_period=request.poll.open_period,
        )
    
    # Создаем признание через контроллер
    try:
        result_dto = await confession_controller.create_confession(confession_dto)
        return ConfessionResponse.model_validate(result_dto.model_dump())
    except Exception as e:
        logger.error(f"Error creating confession: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating confession: {str(e)}",
        )


@router.get("/{confession_id}", response_model=ConfessionResponse)
async def get_confession(
    confession_id: int,
    confession_controller: ConfessionController = Depends(get_confession_controller),
) -> ConfessionResponse:
    """
    Получает признание по ID.
    """
    logger.info(f"Getting confession with ID {confession_id}")
    
    # Создаем пустой DTO с указанным ID
    confession_dto = ConfessionDTO(
        id=confession_id,
        content="",  # Будет заполнено при получении из репозитория
    )
    
    # Пытаемся получить признание через контроллер
    try:
        result_dto = await confession_controller.get_confession(confession_dto)
        if not result_dto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Confession with ID {confession_id} not found",
            )
        return ConfessionResponse.model_validate(result_dto.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting confession: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting confession: {str(e)}",
        )


@router.get("/", response_model=List[ConfessionResponse])
async def list_confessions(
    status_filter: Optional[ConfessionStatus] = Query(None, alias="status", description="Фильтр по статусу признания"),
    confession_controller: ConfessionController = Depends(get_confession_controller),
) -> List[ConfessionResponse]:
    """
    Получает список признаний, опционально отфильтрованный по статусу.
    """
    logger.info(f"Listing confessions with status {status_filter}")
    
    # Пытаемся получить список признаний
    try:
        confession_dtos = await confession_controller.list_by_status(status_filter)
        return [ConfessionResponse.model_validate(confession) for confession in confession_dtos]
    except Exception as e:
        logger.error(f"Error listing confessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing confessions: {str(e)}",
        )


@router.post("/{confession_id}/moderate", response_model=ConfessionResponse)
async def moderate_confession(
    confession_id: int,
    confession_controller: ConfessionController = Depends(get_confession_controller),
) -> ConfessionResponse:
    """
    Отправляет признание на модерацию.
    """
    logger.info(f"Moderating confession with ID {confession_id}")
    
    # Создаем пустой DTO с указанным ID
    confession_dto = ConfessionDTO(
        id=confession_id,
        content="",  # Будет заполнено при получении из репозитория
    )
    
    # Пытаемся модерировать признание
    try:
        # Модерируем признание
        moderation_result = await confession_controller.moderate_confession(confession_dto)
        
        # Получаем обновленные данные признания
        updated_dto = await confession_controller.get_confession(confession_dto)
        
        if not updated_dto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Confession with ID {confession_id} not found after moderation",
            )
        
        return ConfessionResponse.model_validate(updated_dto.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moderating confession: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error moderating confession: {str(e)}",
        )


@router.post("/{confession_id}/publish", response_model=ConfessionResponse)
async def publish_confession(
    confession_id: int,
    confession_controller: ConfessionController = Depends(get_confession_controller),
) -> ConfessionResponse:
    """
    Публикует одобренное признание в Telegram.
    """
    logger.info(f"Publishing confession with ID {confession_id}")
    
    # Создаем пустой DTO с указанным ID
    confession_dto = ConfessionDTO(
        id=confession_id,
        content="",  # Будет заполнено при получении из репозитория
    )
    
    # Пытаемся опубликовать признание
    try:
        result_dto = await confession_controller.publish_confession(confession_dto)
        return ConfessionResponse.model_validate(result_dto.model_dump())
    except ValueError as e:
        # Ошибка валидации (например, признание не одобрено)
        logger.error(f"Validation error when publishing confession: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error publishing confession: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error publishing confession: {str(e)}",
        )


@router.patch("/{confession_id}/status", response_model=ConfessionResponse)
async def update_confession_status(
    confession_id: int,
    status_update: StatusUpdateRequest,
    confession_controller: ConfessionController = Depends(get_confession_controller),
) -> ConfessionResponse:
    """
    Обновляет статус признания.
    """
    logger.info(f"Updating status for confession with ID {confession_id} to {status_update.status}")
    
    # Обновляем статус
    try:
        result_dto = await confession_controller.update_status(confession_id, status_update.status)
        if not result_dto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Confession with ID {confession_id} not found",
            )
        return ConfessionResponse.model_validate(result_dto)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating confession status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating confession status: {str(e)}",
        )