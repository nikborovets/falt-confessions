"""
Тесты для роутера опросов.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient

from src.entities.confession import Confession, Poll, PollOption
from src.entities.enums import ConfessionStatus
from src.frameworks_and_drivers.rest_api.schemas.confession import PollResponse
from src.main import app
from src.interface_adapters.controllers import PollController


@pytest.fixture
def client():
    """Тестовый клиент FastAPI."""
    return TestClient(app)


@pytest.fixture
def poll_controller_mock():
    """Мок контроллера для опросов."""
    # Определяем все методы, которые будем использовать в тестах
    methods = [
        "create_poll",
        "vote",
        "get_results",
    ]
    controller = AsyncMock(spec=methods)
    return controller


@pytest.fixture
def sample_poll():
    """Тестовый опрос."""
    return Poll(
        id=1,
        question="Тестовый вопрос",
        options=[
            PollOption(id=1, text="Вариант 1", vote_count=5),
            PollOption(id=2, text="Вариант 2", vote_count=3),
        ],
    )


@pytest.fixture
def confession_with_poll(sample_poll):
    """Тестовое признание с опросом."""
    return Confession(
        id=1,
        content="Тестовое признание с опросом",
        status=ConfessionStatus.APPROVED,
        created_at=datetime.now(),
        poll=sample_poll,
    )


@pytest.mark.skip("Endpoints are not implemented yet")
@patch("src.frameworks_and_drivers.dependencies.get_poll_controller")
def test_vote_in_poll(get_controller_mock, client, poll_controller_mock, sample_poll):
    """Тест голосования в опросе через API."""
    # Arrange
    get_controller_mock.return_value = poll_controller_mock
    updated_poll = Poll(
        id=1,
        question="Тестовый вопрос",
        options=[
            PollOption(id=1, text="Вариант 1", vote_count=6),  # +1 голос
            PollOption(id=2, text="Вариант 2", vote_count=3),
        ],
    )
    poll_controller_mock.vote.return_value = updated_poll
    
    # Создаем тестовые данные
    vote_data = {
        "option_id": 1,
    }
    
    # Act
    response = client.post("/api/polls/1/vote", json=vote_data)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1
    assert response.json()["question"] == "Тестовый вопрос"
    assert response.json()["options"][0]["vote_count"] == 6
    
    # Проверяем, что контроллер был вызван
    poll_controller_mock.vote.assert_called_once()


@pytest.mark.skip("Endpoints are not implemented yet")
@patch("src.frameworks_and_drivers.dependencies.get_poll_controller")
def test_vote_in_poll_invalid_option(get_controller_mock, client, poll_controller_mock):
    """Тест голосования с неверным вариантом опроса через API."""
    # Arrange
    get_controller_mock.return_value = poll_controller_mock
    poll_controller_mock.vote.side_effect = ValueError("Invalid option id")
    
    # Создаем тестовые данные
    vote_data = {
        "option_id": 999,  # Несуществующий вариант
    }
    
    # Act
    response = client.post("/api/polls/1/vote", json=vote_data)
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Проверяем, что контроллер был вызван
    poll_controller_mock.vote.assert_called_once()


@pytest.mark.skip("Endpoints are not implemented yet")
@patch("src.frameworks_and_drivers.dependencies.get_poll_controller")
def test_get_poll_results(get_controller_mock, client, poll_controller_mock, sample_poll):
    """Тест получения результатов опроса через API."""
    # Arrange
    get_controller_mock.return_value = poll_controller_mock
    poll_controller_mock.get_results.return_value = sample_poll
    
    # Act
    response = client.get("/api/polls/1/results")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1
    assert response.json()["question"] == "Тестовый вопрос"
    assert len(response.json()["options"]) == 2
    assert response.json()["options"][0]["vote_count"] == 5
    assert response.json()["options"][1]["vote_count"] == 3
    
    # Проверяем, что контроллер был вызван
    poll_controller_mock.get_results.assert_called_once()


@pytest.mark.skip("Endpoints are not implemented yet")
@patch("src.frameworks_and_drivers.dependencies.get_poll_controller")
def test_get_poll_results_not_found(get_controller_mock, client, poll_controller_mock):
    """Тест получения результатов несуществующего опроса через API."""
    # Arrange
    get_controller_mock.return_value = poll_controller_mock
    poll_controller_mock.get_results.return_value = None
    
    # Act
    response = client.get("/api/polls/999/results")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Проверяем, что контроллер был вызван
    poll_controller_mock.get_results.assert_called_once()