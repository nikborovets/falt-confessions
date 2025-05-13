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
    TagRequest,
    TagResponse,
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
    "TagRequest",
    "TagResponse",
] 