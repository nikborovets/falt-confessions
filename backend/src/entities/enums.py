"""
Перечисления, используемые в доменных сущностях.
"""
from enum import Enum, auto


class ConfessionStatus(str, Enum):
    """Статус признания."""

    PENDING = "PENDING"  # Ожидает модерации
    APPROVED = "APPROVED"  # Одобрено, но еще не опубликовано
    REJECTED = "REJECTED"  # Отклонено модерацией
    PUBLISHED = "PUBLISHED"  # Опубликовано в Telegram


class AttachmentType(str, Enum):
    """Тип вложения в признании."""

    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    MUSIC = "MUSIC"
    DOCUMENT = "DOCUMENT"
    OTHER = "OTHER" 