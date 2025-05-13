"""
Тесты для сущностей Poll и PollOption.
"""
import pytest
from datetime import datetime

from src.entities.confession import Poll, PollOption


def test_poll_option_creation():
    """Тест создания варианта опроса."""
    # Arrange & Act
    option = PollOption(
        text="Вариант ответа",
        vote_count=0,
    )
    
    # Assert
    assert option.text == "Вариант ответа"
    assert option.vote_count == 0
    assert option.id is None


def test_poll_creation():
    """Тест создания опроса."""
    # Arrange
    options = [
        PollOption(text="Вариант 1"),
        PollOption(text="Вариант 2"),
        PollOption(text="Вариант 3"),
    ]
    
    # Act
    poll = Poll(
        question="Тестовый вопрос",
        options=options,
    )
    
    # Assert
    assert poll.question == "Тестовый вопрос"
    assert len(poll.options) == 3
    assert poll.allows_multiple_answers is False
    assert poll.type == "regular"
    assert poll.id is None
    assert poll.correct_option_id is None
    assert poll.explanation is None
    assert poll.open_period is None


def test_poll_with_quiz_settings():
    """Тест создания опроса-викторины."""
    # Arrange
    options = [
        PollOption(text="Вариант 1"),
        PollOption(text="Вариант 2"),
        PollOption(text="Вариант 3"),
    ]
    
    # Act
    poll = Poll(
        question="Тестовый вопрос",
        options=options,
        type="quiz",
        correct_option_id=1,
        explanation="Правильный ответ - вариант 2",
    )
    
    # Assert
    assert poll.type == "quiz"
    assert poll.correct_option_id == 1
    assert poll.explanation == "Правильный ответ - вариант 2"


def test_poll_with_timing_settings():
    """Тест создания опроса с ограничением по времени."""
    # Arrange
    options = [
        PollOption(text="Вариант 1"),
        PollOption(text="Вариант 2"),
    ]
    
    # Act
    poll = Poll(
        question="Тестовый вопрос",
        options=options,
        open_period=300,  # 5 минут
    )
    
    # Assert
    assert poll.open_period == 300


def test_poll_with_multiple_answers():
    """Тест создания опроса с множественным выбором."""
    # Arrange
    options = [
        PollOption(text="Вариант 1"),
        PollOption(text="Вариант 2"),
        PollOption(text="Вариант 3"),
        PollOption(text="Вариант 4"),
    ]
    
    # Act
    poll = Poll(
        question="Тестовый вопрос множественного выбора",
        options=options,
        allows_multiple_answers=True,
    )
    
    # Assert
    assert poll.allows_multiple_answers is True
    assert len(poll.options) == 4 