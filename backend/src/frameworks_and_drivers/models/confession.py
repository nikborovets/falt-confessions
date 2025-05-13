"""
SQLAlchemy модели для признаний и связанных сущностей.
"""
import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from src.entities.enums import AttachmentType, ConfessionStatus
from src.frameworks_and_drivers.db.database import Base


# Таблица связи между признаниями и тегами
confession_tag = Table(
    "confession_tag",
    Base.metadata,
    Column("confession_id", Integer, ForeignKey("confessions.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class ConfessionModel(Base):
    """ORM-модель для признания."""

    __tablename__ = "confessions"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(Enum(ConfessionStatus), default=ConfessionStatus.PENDING)

    # Отношения
    attachments = relationship("AttachmentModel", back_populates="confession", cascade="all, delete-orphan")
    tags = relationship("TagModel", secondary=confession_tag, back_populates="confessions")
    poll = relationship("PollModel", back_populates="confession", uselist=False, cascade="all, delete-orphan")
    moderation_logs = relationship("ModerationLogModel", back_populates="confession", cascade="all, delete-orphan")
    published_record = relationship(
        "PublishedRecordModel", back_populates="confession", uselist=False, cascade="all, delete-orphan"
    )
    comments = relationship("CommentModel", back_populates="confession", cascade="all, delete-orphan")


class AttachmentModel(Base):
    """ORM-модель для вложения."""

    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    confession_id = Column(Integer, ForeignKey("confessions.id"))
    url = Column(String(255), nullable=False)
    type = Column(Enum(AttachmentType), default=AttachmentType.OTHER)
    uploaded_at = Column(DateTime, default=datetime.now)
    caption = Column(String(255), nullable=True)

    # Отношения
    confession = relationship("ConfessionModel", back_populates="attachments")


class PollOptionModel(Base):
    """ORM-модель для варианта ответа в опросе."""

    __tablename__ = "poll_options"

    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("polls.id"))
    text = Column(String(255), nullable=False)
    vote_count = Column(Integer, default=0)

    # Отношения
    poll = relationship("PollModel", back_populates="options")


class PollModel(Base):
    """ORM-модель для опроса."""

    __tablename__ = "polls"

    id = Column(Integer, primary_key=True, index=True)
    confession_id = Column(Integer, ForeignKey("confessions.id"), unique=True)
    question = Column(String(255), nullable=False)
    allows_multiple_answers = Column(Boolean, default=False)
    type = Column(String(50), default="regular")  # "regular" или "quiz"
    correct_option_id = Column(Integer, nullable=True)
    explanation = Column(String(255), nullable=True)
    open_period = Column(Integer, nullable=True)
    poll_message_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Отношения
    confession = relationship("ConfessionModel", back_populates="poll")
    options = relationship("PollOptionModel", back_populates="poll", cascade="all, delete-orphan")


class TagModel(Base):
    """ORM-модель для тега."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    # Отношения
    confessions = relationship("ConfessionModel", secondary=confession_tag, back_populates="tags")


class ModerationLogModel(Base):
    """ORM-модель для записи о модерации."""

    __tablename__ = "moderation_logs"

    id = Column(Integer, primary_key=True, index=True)
    confession_id = Column(Integer, ForeignKey("confessions.id"))
    decision = Column(Enum(ConfessionStatus), default=ConfessionStatus.PENDING)
    moderator = Column(String(100), nullable=False)  # "LLM" или имя модератора
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.now)

    # Отношения
    confession = relationship("ConfessionModel", back_populates="moderation_logs")


class PublishedRecordModel(Base):
    """ORM-модель для информации о публикации."""

    __tablename__ = "published_records"

    id = Column(Integer, primary_key=True, index=True)
    confession_id = Column(Integer, ForeignKey("confessions.id"), unique=True)
    telegram_message_id = Column(String(50), nullable=False)
    channel_id = Column(String(100), nullable=False)
    published_at = Column(DateTime, default=datetime.now)
    discussion_thread_id = Column(String(50), nullable=True)

    # Отношения
    confession = relationship("ConfessionModel", back_populates="published_record")


class CommentModel(Base):
    """ORM-модель для комментария."""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    confession_id = Column(Integer, ForeignKey("confessions.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    reply_to = Column(Integer, ForeignKey("comments.id"), nullable=True)

    # Отношения
    confession = relationship("ConfessionModel", back_populates="comments")
    replies = relationship("CommentModel", back_populates="parent", remote_side=[id])
    parent = relationship("CommentModel", back_populates="replies", remote_side=[reply_to]) 