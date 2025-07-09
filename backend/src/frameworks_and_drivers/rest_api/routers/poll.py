"""
Роутер для работы с опросами.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from src.frameworks_and_drivers.dependencies import get_poll_controller
from src.frameworks_and_drivers.rest_api.schemas import PollRequest, PollResponse, VoteRequest
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


@router.post("/{poll_id}/vote", response_model=PollResponse)
async def vote_in_poll(
    poll_id: int,
    request: VoteRequest,
    poll_controller: PollController = Depends(get_poll_controller),
) -> PollResponse:
    """
    Голосование в опросе.
    """
    logger.info(f"Voting in poll {poll_id}, option {request.option_id}")
    
    # Пытаемся проголосовать
    try:
        result_poll = await poll_controller.vote(poll_id, request.option_id)
        if not result_poll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Poll with ID {poll_id} not found",
            )
        return PollResponse.model_validate(result_poll.model_dump())
    except ValueError as e:
        # Ошибка валидации (например, неверный ID варианта)
        logger.error(f"Validation error when voting in poll: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error voting in poll: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error voting in poll: {str(e)}",
        )


@router.get("/{poll_id}/results", response_model=PollResponse)
async def get_poll_results(
    poll_id: int,
    poll_controller: PollController = Depends(get_poll_controller),
) -> PollResponse:
    """
    Получает результаты опроса.
    """
    logger.info(f"Getting results for poll {poll_id}")
    
    # Пытаемся получить результаты
    try:
        poll = await poll_controller.get_results(poll_id)
        if not poll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Poll with ID {poll_id} not found",
            )
        return PollResponse.model_validate(poll.model_dump())
    except Exception as e:
        logger.error(f"Error getting poll results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting poll results: {str(e)}",
        ) 