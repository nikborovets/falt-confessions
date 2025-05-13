"""
Тесты для сущности Tag.
"""
import pytest

from src.entities.confession import Tag, Confession


def test_tag_creation():
    """Тест создания тега."""
    # Arrange & Act
    tag = Tag(name="тест")
    
    # Assert
    assert tag.name == "тест"
    assert tag.id is None


def test_tag_with_id():
    """Тест создания тега с ID."""
    # Arrange & Act
    tag = Tag(id=123, name="категория")
    
    # Assert
    assert tag.id == 123
    assert tag.name == "категория"


def test_confession_with_tags():
    """Тест создания признания с тегами."""
    # Arrange
    tags = [
        Tag(name="анонимно"),
        Tag(name="история"),
        Tag(name="смешное"),
    ]
    
    # Act
    confession = Confession(
        content="Тестовое признание с тегами",
        tags=tags,
    )
    
    # Assert
    assert len(confession.tags) == 3
    assert confession.tags[0].name == "анонимно"
    assert confession.tags[1].name == "история"
    assert confession.tags[2].name == "смешное" 