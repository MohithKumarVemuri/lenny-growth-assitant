import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")
    artifacts = relationship("Artifact", back_populates="session", cascade="all, delete-orphan", order_by="Artifact.created_at")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # 'user' | 'assistant' | 'system'
    content = Column(Text, nullable=False)
    sources = Column(JSON, default=list)  # List of {episode, guest, timestamp, score, text}
    model_provider = Column(String(50), default="ollama")
    mode = Column(String(50), default="default")  # 'default' | 'ship30' | 'artifact'
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    session = relationship("Session", back_populates="messages")
    artifacts = relationship("Artifact", back_populates="message", cascade="all, delete-orphan")

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    artifact_type = Column(String(50), nullable=False)  # 'html' | 'markdown'
    content = Column(Text, nullable=False)
    language = Column(String(50), default="html")
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    session = relationship("Session", back_populates="artifacts")
    message = relationship("Message", back_populates="artifacts")

class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    episode_title = Column(String(255), nullable=False)
    guest_name = Column(String(255), nullable=False)
    episode_url = Column(String(512), nullable=True)
    timestamp_ref = Column(String(100), nullable=True)
    chunk_text = Column(Text, nullable=False)
    embedding_json = Column(Text, nullable=False)  # JSON-encoded float list for portability
