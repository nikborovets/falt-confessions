"""
Тесты для роутера признаний.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient

from src.entities.confession import Confession, Poll, PollOption, Tag
from src.entities.enums import AttachmentType, ConfessionStatus
from src.frameworks_and_drivers.rest_api.schemas.confession import (
    ConfessionRequest,
    ConfessionResponse,
)
from src.main import app
from src.interface_adapters.controllers import ConfessionController


@pytest.fixture
def client():
    """Тестовый клиент FastAPI."""
    return TestClient(app)


@pytest.fixture
def confession_controller_mock():
    """Мок контроллера для признаний."""
    # Определяем все методы, которые будем использовать в тестах
    methods = [
        "create_confession",
        "get_confession",
        "list_confessions",
        "update_status",
        "moderate_confession",
        "publish_confession",
        "list_by_status",
    ]
    controller = AsyncMock(spec=methods)
    return controller


@pytest.fixture
def sample_confession():
    """Тестовое признание."""
    return Confession(
        id=1,
        content="Тестовое признание через API",
        status=ConfessionStatus.PENDING,
        created_at=datetime.now(),
    )


@pytest.fixture
def confession_with_poll():
    """Тестовое признание с опросом."""
    return Confession(
        id=2,
        content="Тестовое признание с опросом через API",
        status=ConfessionStatus.PENDING,
        created_at=datetime.now(),
        poll=Poll(
            question="Тестовый вопрос",
            options=[
                PollOption(text="Вариант 1"),
                PollOption(text="Вариант 2"),
            ],
        ),
    )


@pytest.mark.skip("Endpoints are not implemented yet")
@patch("src.frameworks_and_drivers.dependencies.get_confession_controller")
def test_create_confession(get_controller_mock, client, confession_controller_mock, sample_confession):
    """Тест создания признания через API."""
    # Arrange
    get_controller_mock.return_value = confession_controller_mock
    confession_controller_mock.create_confession.return_value = sample_confession
    
    # Создаем тестовые данные
    confession_data = {
        "content": "Тестовое признание через API",
        "tags": ["тест", "api"],
    }
    
    # Act
    response = client.post("/api/confessions/", json=confession_data)
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] == 1
    assert response.json()["content"] == sample_confession.content
    assert response.json()["status"] == sample_confession.status.value
    
    # Проверяем, что контроллер был вызван
    confession_controller_mock.create_confession.assert_called_once()


@pytest.mark.skip("Endpoints are not implemented yet")
@patch("src.frameworks_and_drivers.dependencies.get_confession_controller")
def test_create_confession_with_poll(get_controller_mock, client, confession_controller_mock, confession_with_poll):
    """Тест создания признания с опросом через API."""
    # Arrange
    get_controller_mock.return_value = confession_controller_mock
    confession_controller_mock.create_confession.return_value = confession_with_poll
    
    # Создаем тестовые данные
    confession_data = {
        "content": "Тестовое признание с опросом через API",
        "tags": ["тест", "api", "опрос"],
        "poll": {
            "question": "Тестовый вопрос",
            "options": [
                {"text": "Вариант 1"},
                {"text": "Вариант 2"},
            ],
        },
    }
    
    # Act
    response = client.post("/api/confessions/", json=confession_data)
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] == 2
    assert response.json()["content"] == confession_with_poll.content
    assert response.json()["status"] == confession_with_poll.status.value
    assert response.json()["poll"]["question"] == confession_with_poll.poll.question
    assert len(response.json()["poll"]["options"]) == 2
    
    # Проверяем, что контроллер был вызван
    confession_controller_mock.create_confession.assert_called_once()


@pytest.mark.skip("Endpoints are not implemented yet")
@patch("src.frameworks_and_drivers.dependencies.get_confession_controller")
def test_get_confession_by_id(get_controller_mock, client, confession_controller_mock, sample_confession):
    """Тест получения признания по ID через API."""
    # Arrange
    get_controller_mock.return_value = confession_controller_mock
    confession_controller_mock.get_confession.return_value = sample_confession
    
    # Act
    response = client.get("/api/confessions/1")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1
    assert response.json()["content"] == sample_confession.content
    
    # Проверяем, что контроллер был вызван
    confession_controller_mock.get_confession.assert_called_once()


@pytest.mark.skip("Endpoints are not implemented yet")
@patch("src.frameworks_and_drivers.dependencies.get_confession_controller")
def test_get_confession_by_id_not_found(get_controller_mock, client, confession_controller_mock):
    """Тест получения несуществующего признания по ID через API."""
    # Arrange
    get_controller_mock.return_value = confession_controller_mock
    confession_controller_mock.get_confession.return_value = None
    
    # Act
    response = client.get("/api/confessions/999")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Проверяем, что контроллер был вызван
    confession_controller_mock.get_confession.assert_called_once()


@pytest.mark.skip("Endpoints are not implemented yet")
@patch("src.frameworks_and_drivers.dependencies.get_confession_controller")
def test_update_confession_status(get_controller_mock, client, confession_controller_mock, sample_confession):
    """Тест обновления статуса признания через API."""
    # Arrange
    get_controller_mock.return_value = confession_controller_mock
    sample_confession.status = ConfessionStatus.APPROVED
    confession_controller_mock.update_status.return_value = sample_confession
    
    # Создаем тестовые данные
    status_data = {
        "status": "APPROVED",
    }
    
    # Act
    response = client.patch("/api/confessions/1/status", json=status_data)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1
    assert response.json()["status"] == ConfessionStatus.APPROVED.value
    
    # Проверяем, что контроллер был вызван
    confession_controller_mock.update_status.assert_called_once()


@pytest.mark.skip("Endpoints are not implemented yet")
@patch("src.frameworks_and_drivers.dependencies.get_confession_controller")
def test_get_confessions_by_status(get_controller_mock, client, confession_controller_mock, sample_confession):
    """Тест получения списка признаний по статусу через API."""
    # Arrange
    get_controller_mock.return_value = confession_controller_mock
    confession_controller_mock.list_by_status.return_value = [sample_confession]
    
    # Act
    response = client.get("/api/confessions/?status=PENDING")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == 1
    assert response.json()[0]["status"] == ConfessionStatus.PENDING.value
    
    # Проверяем, что контроллер был вызван
    confession_controller_mock.list_by_status.assert_called_once()