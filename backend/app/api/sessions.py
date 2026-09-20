import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.db_models import Session, Message, Artifact
from app.models.schemas import SessionCreate, SessionResponse, SessionDetailResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(payload: SessionCreate, db: AsyncSession = Depends(get_db)):
    new_session = Session(title=payload.title or "New Conversation")
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session

@router.get("", response_model=List[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    stmt = select(Session).order_by(Session.updated_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Session)
        .where(Session.id == session_id)
        .options(
            selectinload(Session.messages).selectinload(Message.artifacts),
            selectinload(Session.artifacts)
        )
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Session).where(Session.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(session)
    await db.commit()
    return None

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_all_sessions(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Session))
    await db.commit()
    return None
