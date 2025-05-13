"""
Тесты для сущности Attachment.
"""
import pytest
from datetime import datetime

from src.entities.confession import Attachment
from src.entities.enums import AttachmentType


def test_attachment_creation():
    """Тест создания вложения."""
    # Arrange & Act
    attachment = Attachment(
        url="https://example.com/image.jpg",
        type=AttachmentType.IMAGE,
    )
    
    # Assert
    assert attachment.url == "https://example.com/image.jpg"
    assert attachment.type == AttachmentType.IMAGE
    assert attachment.id is None
    assert attachment.caption is None
    assert isinstance(attachment.uploaded_at, datetime)


def test_attachment_with_caption():
    """Тест создания вложения с подписью."""
    # Arrange & Act
    attachment = Attachment(
        url="https://example.com/doc.pdf",
        type=AttachmentType.DOCUMENT,
        caption="Важный документ",
    )
    
    # Assert
    assert attachment.url == "https://example.com/doc.pdf"
    assert attachment.type == AttachmentType.DOCUMENT
    assert attachment.caption == "Важный документ"


def test_attachment_with_timestamp():
    """Тест создания вложения с указанием времени загрузки."""
    # Arrange
    timestamp = datetime(2023, 5, 15, 14, 30, 0)
    
    # Act
    attachment = Attachment(
        id=1,
        url="https://example.com/video.mp4",
        type=AttachmentType.VIDEO,
        uploaded_at=timestamp,
    )
    
    # Assert
    assert attachment.id == 1
    assert attachment.url == "https://example.com/video.mp4"
    assert attachment.type == AttachmentType.VIDEO
    assert attachment.uploaded_at == timestamp 