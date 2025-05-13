"""
Тесты для сущности Comment.
"""
import pytest
from datetime import datetime

from src.entities.confession import Comment


def test_comment_creation():
    """Тест создания комментария."""
    # Arrange & Act
    comment = Comment(
        confession_id=1,
        content="Тестовый комментарий",
    )
    
    # Assert
    assert comment.confession_id == 1
    assert comment.content == "Тестовый комментарий"
    assert comment.id is None
    assert comment.reply_to is None
    assert isinstance(comment.created_at, datetime)


def test_comment_reply():
    """Тест создания комментария-ответа."""
    # Arrange & Act
    comment = Comment(
        confession_id=1,
        content="Ответ на комментарий",
        reply_to=5,  # ID родительского комментария
    )
    
    # Assert
    assert comment.confession_id == 1
    assert comment.content == "Ответ на комментарий"
    assert comment.reply_to == 5


def test_comment_with_timestamp():
    """Тест создания комментария с указанием времени."""
    # Arrange
    timestamp = datetime(2023, 5, 15, 16, 30, 0)
    
    # Act
    comment = Comment(
        id=10,
        confession_id=2,
        content="Комментарий с временной меткой",
        created_at=timestamp,
    )
    
    # Assert
    assert comment.id == 10
    assert comment.confession_id == 2
    assert comment.content == "Комментарий с временной меткой"
    assert comment.created_at == timestamp 