"""
Роутер для работы с опросами.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from src.frameworks_and_drivers.dependencies import get_poll_controller
from src.frameworks_and_drivers.rest_api.schemas import PollRequest, PollResponse
from src.interface_adapters.controllers import PollController
from src.interface_adapters.dto import PollDTO, PollOptionDTO

router = APIRouter(prefix="/polls", tags=["polls"])


@router.post("/", response_model=PollResponse, status_code=status.HTTP_201_CREATED)
async def post_poll(
    request: PollRequest,
    poll_controller: PollController = Depends(get_poll_controller),
) -> PollResponse:
    """
    Создает новый опрос.
    """
    logger.info(f"Creating new poll: {request.question}")
    
    # Преобразуем запрос в DTO
    poll_dto = PollDTO(
        question=request.question,
        options=[
            PollOptionDTO(text=option.text)
            for option in request.options
        ],
        allows_multiple_answers=request.allows_multiple_answers,
        type=request.type,
        correct_option_id=request.correct_option_id,
        explanation=request.explanation,
        open_period=request.open_period,
    )
    
    # Создаем опрос через контроллер
    try:
        result_dto = await poll_controller.create_poll(poll_dto)
        return PollResponse.model_validate(result_dto.model_dump())
    except Exception as e:
        logger.error(f"Error creating poll: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating poll: {str(e)}",
        ) 