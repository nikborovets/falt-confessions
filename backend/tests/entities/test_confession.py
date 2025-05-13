"""
Тесты для сущности Confession.
"""
import pytest
from datetime import datetime

from src.entities.confession import Confession, Attachment, Tag, Poll, PollOption
from src.entities.enums import ConfessionStatus, AttachmentType


def test_confession_creation():
    """Тест создания простого признания."""
    # Arrange
    content = "Тестовое признание"
    
    # Act
    confession = Confession(content=content)
    
    # Assert
    assert confession.content == content
    assert confession.status == ConfessionStatus.PENDING
    assert confession.id is None
    assert len(confession.attachments) == 0
    assert len(confession.tags) == 0
    assert confession.poll is None


def test_confession_with_attachments():
    """Тест создания признания с вложениями."""
    # Arrange
    content = "Признание с вложениями"
    attachments = [
        Attachment(
            url="https://example.com/image1.jpg",
            type=AttachmentType.IMAGE,
            caption="Изображение 1",
        ),
        Attachment(
            url="https://example.com/image2.jpg",
            type=AttachmentType.IMAGE,
            caption="Изображение 2",
        ),
    ]
    
    # Act
    confession = Confession(
        content=content,
        attachments=attachments,
    )
    
    # Assert
    assert confession.content == content
    assert len(confession.attachments) == 2
    assert confession.attachments[0].url == "https://example.com/image1.jpg"
    assert confession.attachments[0].type == AttachmentType.IMAGE
    assert confession.attachments[0].caption == "Изображение 1"
    assert confession.attachments[1].url == "https://example.com/image2.jpg"


def test_confession_with_tags():
    """Тест создания признания с тегами."""
    # Arrange
    content = "Признание с тегами"
    tags = [
        Tag(name="тег1"),
        Tag(name="тег2"),
        Tag(name="тег3"),
    ]
    
    # Act
    confession = Confession(
        content=content,
        tags=tags,
    )
    
    # Assert
    assert confession.content == content
    assert len(confession.tags) == 3
    assert confession.tags[0].name == "тег1"
    assert confession.tags[1].name == "тег2"
    assert confession.tags[2].name == "тег3"


def test_confession_with_poll():
    """Тест создания признания с опросом."""
    # Arrange
    content = "Признание с опросом"
    poll_options = [
        PollOption(text="Вариант 1"),
        PollOption(text="Вариант 2"),
        PollOption(text="Вариант 3"),
    ]
    poll = Poll(
        question="Тестовый вопрос",
        options=poll_options,
        allows_multiple_answers=True,
    )
    
    # Act
    confession = Confession(
        content=content,
        poll=poll,
    )
    
    # Assert
    assert confession.content == content
    assert confession.poll is not None
    assert confession.poll.question == "Тестовый вопрос"
    assert len(confession.poll.options) == 3
    assert confession.poll.options[0].text == "Вариант 1"
    assert confession.poll.allows_multiple_answers is True 