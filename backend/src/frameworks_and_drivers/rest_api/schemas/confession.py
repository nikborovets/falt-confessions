"""
Pydantic-схемы для API признаний и связанных сущностей.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.entities.enums import AttachmentType, ConfessionStatus


class TagRequest(BaseModel):
    """Схема запроса для тега."""
    
    name: str = Field(..., min_length=1, max_length=50)


class TagResponse(BaseModel):
    """Схема ответа для тега."""
    
    id: int
    name: str


class AttachmentRequest(BaseModel):
    """Схема запроса для вложения."""
    
    url: str = Field(..., min_length=1, max_length=255)
    type: AttachmentType
    caption: Optional[str] = Field(None, max_length=255)


class AttachmentResponse(BaseModel):
    """Схема ответа для вложения."""
    
    id: int
    url: str
    type: AttachmentType
    uploaded_at: datetime
    caption: Optional[str] = None


class PollOptionRequest(BaseModel):
    """Схема запроса для варианта опроса."""
    
    text: str = Field(..., min_length=1, max_length=255)


class PollOptionResponse(BaseModel):
    """Схема ответа для варианта опроса."""
    
    id: int
    text: str
    vote_count: int


class PollRequest(BaseModel):
    """Схема запроса для опроса."""
    
    question: str = Field(..., min_length=1, max_length=255)
    options: List[PollOptionRequest] = Field(..., min_length=2, max_length=10)
    allows_multiple_answers: bool = False
    type: str = "regular"
    correct_option_id: Optional[int] = None
    explanation: Optional[str] = None
    open_period: Optional[int] = None


class PollResponse(BaseModel):
    """Схема ответа для опроса."""
    
    id: int
    question: str
    options: List[PollOptionResponse]
    allows_multiple_answers: bool
    type: str
    correct_option_id: Optional[int] = None
    explanation: Optional[str] = None
    open_period: Optional[int] = None
    created_at: datetime


class VoteRequest(BaseModel):
    """Схема запроса для голосования в опросе."""
    
    option_id: int = Field(..., description="ID варианта ответа")


class StatusUpdateRequest(BaseModel):
    """Схема запроса для обновления статуса признания."""
    
    status: ConfessionStatus = Field(..., description="Новый статус признания")


class ConfessionRequest(BaseModel):
    """Схема запроса для создания признания."""
    
    content: str = Field(..., min_length=1, max_length=5000)
    attachments: List[AttachmentRequest] = Field(default_factory=list)
    tags: List[TagRequest] = Field(default_factory=list)
    poll: Optional[PollRequest] = None


class ConfessionResponse(BaseModel):
    """Схема ответа с признанием."""
    
    id: int
    content: str
    created_at: datetime
    status: ConfessionStatus
    attachments: List[AttachmentResponse] = Field(default_factory=list)
    tags: List[TagResponse] = Field(default_factory=list)
    poll: Optional[PollResponse] = None
    
    model_config = ConfigDict(from_attributes=True)