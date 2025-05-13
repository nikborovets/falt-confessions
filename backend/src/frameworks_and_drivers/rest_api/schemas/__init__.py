"""
Pydantic-схемы для FastAPI.
"""

from src.frameworks_and_drivers.rest_api.schemas.confession import (
    AttachmentRequest,
    AttachmentResponse,
    ConfessionRequest,
    ConfessionResponse,
    PollOptionRequest,
    PollOptionResponse,
    PollRequest,
    PollResponse,
    StatusUpdateRequest,
    TagRequest,
    TagResponse,
    VoteRequest,
)

__all__ = [
    "ConfessionRequest",
    "ConfessionResponse",
    "AttachmentRequest",
    "AttachmentResponse",
    "PollRequest",
    "PollResponse",
    "PollOptionRequest",
    "PollOptionResponse",
    "StatusUpdateRequest",
    "TagRequest",
    "TagResponse",
    "VoteRequest",
]