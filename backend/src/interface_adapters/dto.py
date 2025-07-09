"""
DTO-классы (Data Transfer Objects) для передачи данных между слоями.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.entities.enums import AttachmentType, ConfessionStatus


class AttachmentDTO(BaseModel):
    """DTO для вложения к признанию."""
    
    id: Optional[int] = None
    url: str
    type: AttachmentType
    uploaded_at: datetime = Field(default_factory=datetime.now)
    caption: Optional[str] = None


class PollOptionDTO(BaseModel):
    """DTO для варианта ответа в опросе."""
    
    id: Optional[int] = None
    text: str
    vote_count: int = 0


class PollDTO(BaseModel):
    """DTO для опроса."""
    
    id: Optional[int] = None
    question: str
    options: List[PollOptionDTO]
    allows_multiple_answers: bool = False
    type: str = "regular"
    correct_option_id: Optional[int] = None
    explanation: Optional[str] = None
    open_period: Optional[int] = None
    poll_message_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class TagDTO(BaseModel):
    """DTO для тега."""
    
    id: Optional[int] = None
    name: str


class ConfessionDTO(BaseModel):
    """DTO для признания."""
    
    id: Optional[int] = None
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    status: ConfessionStatus = ConfessionStatus.PENDING
    attachments: List[AttachmentDTO] = Field(default_factory=list)
    tags: List[TagDTO] = Field(default_factory=list)
    poll: Optional[PollDTO] = None


class ModerationLogDTO(BaseModel):
    """DTO для записи о модерации."""
    
    id: Optional[int] = None
    confession_id: int
    decision: ConfessionStatus
    moderator: str
    reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class PublishedRecordDTO(BaseModel):
    """DTO для информации о публикации."""
    
    id: Optional[int] = None
    confession_id: int
    telegram_message_id: str
    channel_id: str
    published_at: datetime = Field(default_factory=datetime.now)
    discussion_thread_id: Optional[str] = None


class CommentDTO(BaseModel):
    """DTO для комментария."""
    
    id: Optional[int] = None
    confession_id: int
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    reply_to: Optional[int] = None 