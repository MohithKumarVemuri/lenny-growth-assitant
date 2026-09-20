from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Citations ---
class SourceCitation(BaseModel):
    episode: str
    guest: str
    timestamp: Optional[str] = None
    score: float
    text: str
    url: Optional[str] = None

# --- Artifacts ---
class ArtifactResponse(BaseModel):
    id: str
    session_id: str
    message_id: Optional[str] = None
    title: str
    artifact_type: str  # 'html' | 'markdown'
    content: str
    language: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Messages ---
class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    sources: List[SourceCitation] = []
    model_provider: str
    mode: str
    created_at: datetime
    artifacts: List[ArtifactResponse] = []

    class Config:
        from_attributes = True

# --- Sessions ---
class SessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SessionDetailResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    artifacts: List[ArtifactResponse] = []

    class Config:
        from_attributes = True

# --- Chat Stream Request ---
class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1)
    provider: Optional[str] = None  # 'ollama' | 'claude' | 'openai'
    mode: Optional[str] = "default"  # 'default' | 'ship30' | 'artifact'

# --- Health Probe ---
class HealthResponse(BaseModel):
    status: str
    database_mode: str
    vector_count: int
    default_provider: str
    ollama_status: Dict[str, Any]
    cloud_configured: Dict[str, bool]
