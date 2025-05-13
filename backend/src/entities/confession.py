"""
Доменные сущности для работы с признаниями.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from src.entities.enums import AttachmentType, ConfessionStatus


@dataclass
class Attachment:
    """Вложение к признанию (изображение, видео, аудио и т.д.)."""

    id: Optional[int] = None
    url: str = ""
    type: AttachmentType = AttachmentType.OTHER
    uploaded_at: datetime = field(default_factory=datetime.now)
    caption: Optional[str] = None


@dataclass
class PollOption:
    """Вариант ответа в опросе."""

    id: Optional[int] = None
    text: str = ""
    vote_count: int = 0


@dataclass
class Poll:
    """Опрос, связанный с признанием."""

    id: Optional[int] = None
    question: str = ""
    options: List[PollOption] = field(default_factory=list)
    allows_multiple_answers: bool = False
    type: str = "regular"  # "regular" или "quiz"
    correct_option_id: Optional[int] = None
    explanation: Optional[str] = None
    open_period: Optional[int] = None
    poll_message_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Tag:
    """Тег для категоризации признаний."""

    id: Optional[int] = None
    name: str = ""


@dataclass
class ModerationLog:
    """Запись о модерации признания."""

    id: Optional[int] = None
    confession_id: Optional[int] = None
    decision: ConfessionStatus = ConfessionStatus.PENDING
    moderator: str = ""  # Может быть "LLM" или имя модератора
    reason: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PublishedRecord:
    """Информация о публикации признания в Telegram."""

    id: Optional[int] = None
    confession_id: Optional[int] = None
    telegram_message_id: str = ""
    channel_id: str = ""
    published_at: datetime = field(default_factory=datetime.now)
    discussion_thread_id: Optional[str] = None


@dataclass
class Comment:
    """Комментарий к признанию."""

    id: Optional[int] = None
    confession_id: Optional[int] = None
    content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    reply_to: Optional[int] = None  # ID родительского комментария


@dataclass
class Confession:
    """Основная сущность - признание."""

    id: Optional[int] = None
    content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    status: ConfessionStatus = ConfessionStatus.PENDING
    attachments: List[Attachment] = field(default_factory=list)
    tags: List[Tag] = field(default_factory=list)
    poll: Optional[Poll] = None
    moderation_logs: List[ModerationLog] = field(default_factory=list)
    published_record: Optional[PublishedRecord] = None
    comments: List[Comment] = field(default_factory=list) 