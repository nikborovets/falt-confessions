"""
Тесты для сущности ModerationLog.
"""
import pytest
from datetime import datetime

from src.entities.confession import ModerationLog
from src.entities.enums import ConfessionStatus


def test_moderation_log_creation():
    """Тест создания записи о модерации."""
    # Arrange & Act
    log = ModerationLog(
        confession_id=1,
        decision=ConfessionStatus.APPROVED,
        moderator="LLM",
    )
    
    # Assert
    assert log.confession_id == 1
    assert log.decision == ConfessionStatus.APPROVED
    assert log.moderator == "LLM"
    assert log.reason is None
    assert log.id is None
    assert isinstance(log.timestamp, datetime)


def test_moderation_log_with_reason():
    """Тест создания записи о модерации с причиной отклонения."""
    # Arrange & Act
    log = ModerationLog(
        confession_id=2,
        decision=ConfessionStatus.REJECTED,
        moderator="Администратор",
        reason="Нарушение правил сообщества",
    )
    
    # Assert
    assert log.confession_id == 2
    assert log.decision == ConfessionStatus.REJECTED
    assert log.moderator == "Администратор"
    assert log.reason == "Нарушение правил сообщества"


def test_moderation_log_with_timestamp():
    """Тест создания записи о модерации с указанием времени."""
    # Arrange
    timestamp = datetime(2023, 5, 15, 12, 30, 0)
    
    # Act
    log = ModerationLog(
        confession_id=3,
        decision=ConfessionStatus.PENDING,
        moderator="Система",
        timestamp=timestamp,
    )
    
    # Assert
    assert log.confession_id == 3
    assert log.decision == ConfessionStatus.PENDING
    assert log.moderator == "Система"
    assert log.timestamp == timestamp 