"""
Тесты для сущности PublishedRecord.
"""
import pytest
from datetime import datetime

from src.entities.confession import PublishedRecord


def test_published_record_creation():
    """Тест создания записи о публикации."""
    # Arrange & Act
    record = PublishedRecord(
        confession_id=1,
        telegram_message_id="12345",
        channel_id="@falt_conf",
    )
    
    # Assert
    assert record.confession_id == 1
    assert record.telegram_message_id == "12345"
    assert record.channel_id == "@falt_conf"
    assert record.id is None
    assert record.discussion_thread_id is None
    assert isinstance(record.published_at, datetime)


def test_published_record_with_thread():
    """Тест создания записи о публикации с веткой обсуждения."""
    # Arrange & Act
    record = PublishedRecord(
        confession_id=2,
        telegram_message_id="67890",
        channel_id="@falt_conf",
        discussion_thread_id="thread_123",
    )
    
    # Assert
    assert record.confession_id == 2
    assert record.telegram_message_id == "67890"
    assert record.channel_id == "@falt_conf"
    assert record.discussion_thread_id == "thread_123"


def test_published_record_with_timestamp():
    """Тест создания записи о публикации с указанием времени."""
    # Arrange
    timestamp = datetime(2023, 5, 15, 15, 0, 0)
    
    # Act
    record = PublishedRecord(
        confession_id=3,
        telegram_message_id="abcde",
        channel_id="@falt_conf_test",
        published_at=timestamp,
    )
    
    # Assert
    assert record.confession_id == 3
    assert record.telegram_message_id == "abcde"
    assert record.channel_id == "@falt_conf_test"
    assert record.published_at == timestamp 