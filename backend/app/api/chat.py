import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.db_models import Session, Message, Artifact
from app.models.schemas import ChatRequest
from app.rag.retriever import TranscriptRetriever
from app.providers.factory import get_llm_provider
from app.providers.base import BaseLLMProvider
from app.skills.ship30_writer import build_ship30_prompt
from app.skills.artifact_generator import ARTIFACT_SYSTEM_INSTRUCTIONS, extract_artifact
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat & Streaming"])

DEFAULT_GROUNDED_SYSTEM_PROMPT = """
You are the Lenny Growth Assistant, an authoritative AI product and growth strategist.
Your knowledge is strictly grounded in the provided transcripts from Lenny's Podcast.

### Instructions:
1. Ground every claim, framework, metric, and tactic strictly in the provided transcript context.
2. Explicitly cite the episode and guest name when presenting an insight (e.g. "[Source 1] Brian Chesky on Founder Mode").
3. If the provided context does NOT contain enough information to answer the user's question, acknowledge it directly and say:
   "I do not have sufficient information in Lenny's podcast archive to answer this."
4. Be structured, concise, and highly actionable.
"""

@router.post("")
async def stream_chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    # 1. Verify session
    stmt = select(Session).where(Session.id == req.session_id)
    result = await db.execute(stmt)
    session_obj = result.scalar_one_or_none()
    if not session_obj:
        # Auto-create session if not found
        session_obj = Session(id=req.session_id, title=req.message[:50])
        db.add(session_obj)
        await db.commit()
    elif session_obj.title == "New Conversation":
        # Update title based on first query
        session_obj.title = req.message[:50]
        await db.commit()

    # 2. Persist user message
    user_msg = Message(
        session_id=req.session_id,
        role="user",
        content=req.message,
        mode=req.mode or "default",
        model_provider=req.provider or settings.DEFAULT_PROVIDER
    )
    db.add(user_msg)
    await db.commit()
    await db.refresh(user_msg)

    # 3. Retrieve relevant chunks
    retriever = TranscriptRetriever(db)
    retrieved_chunks = await retriever.retrieve_relevant_chunks(
        query=req.message,
        top_k=settings.TOP_K_RETRIEVAL,
        similarity_threshold=settings.SIMILARITY_THRESHOLD
    )
    formatted_context = retriever.format_grounded_context(retrieved_chunks)

    # 4. Determine system prompt and prompt mode
    mode = (req.mode or "default").lower()
    if mode == "ship30":
        system_prompt = build_ship30_prompt(req.message, formatted_context)
    elif mode == "artifact":
        system_prompt = (
            f"{DEFAULT_GROUNDED_SYSTEM_PROMPT}\n\n"
            f"{ARTIFACT_SYSTEM_INSTRUCTIONS}\n\n"
            f"### Transcript Context:\n{formatted_context}"
        )
    else:
        # Default grounded Q&A with artifact support
        system_prompt = (
            f"{DEFAULT_GROUNDED_SYSTEM_PROMPT}\n\n"
            f"{ARTIFACT_SYSTEM_INSTRUCTIONS}\n\n"
            f"### Transcript Context from Lenny's Podcast:\n{formatted_context}"
        )

    # 5. Fetch past messages for conversational history
    hist_stmt = (
        select(Message)
        .where(Message.session_id == req.session_id)
        .order_by(Message.created_at.asc())
    )
    hist_res = await db.execute(hist_stmt)
    past_messages = [
        {"role": m.role, "content": m.content}
        for m in hist_res.scalars().all()
    ]

    # 6. Select LLM Provider
    provider = get_llm_provider(req.provider)
    is_available = await provider.is_available()
    if not is_available:
        # If requested provider is not available, try fallback simulation provider
        logger.warning(f"Provider {provider.name} unavailable. Falling back to simulation provider.")
        provider = get_llm_provider("sim")

    # 7. SSE Event Streaming Generator
    async def event_generator():
        yield f"data: {json.dumps({'type': 'status', 'content': f'Searching transcripts & routing to {provider.name}...' })}\n\n"

        # Emit citation sources payload
        citation_payload = [
            {
                "episode": c["episode"],
                "guest": c["guest"],
                "timestamp": c["timestamp"],
                "score": c["score"],
                "text": c["text"][:300] + ("..." if len(c["text"]) > 300 else ""),
                "url": c.get("url")
            }
            for c in retrieved_chunks
        ]
        yield f"data: {json.dumps({'type': 'sources', 'sources': citation_payload})}\n\n"

        full_response_text = ""
        try:
            async for token in provider.generate_response(past_messages, system_prompt):
                full_response_text += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        except Exception as e:
            logger.error(f"Error during token generation: {e}")
            yield f"data: {json.dumps({'type': 'token', 'content': f' [Error generating response: {str(e)}]' })}\n\n"

        # Extract artifact if present
        detected_artifact = extract_artifact(full_response_text)
        artifact_record = None
        if detected_artifact:
            try:
                artifact_record = Artifact(
                    session_id=req.session_id,
                    title=detected_artifact["title"],
                    artifact_type=detected_artifact["type"],
                    content=detected_artifact["content"],
                    language=detected_artifact["type"]
                )
                db.add(artifact_record)
                await db.commit()
                await db.refresh(artifact_record)

                yield f"data: {json.dumps({'type': 'artifact', 'artifact': {'id': artifact_record.id, 'title': artifact_record.title, 'type': artifact_record.artifact_type, 'content': artifact_record.content, 'language': artifact_record.language }})}\n\n"
            except Exception as e:
                logger.error(f"Error saving artifact: {e}")

        # Save assistant message to database
        try:
            assistant_msg = Message(
                session_id=req.session_id,
                role="assistant",
                content=full_response_text,
                sources=citation_payload,
                mode=mode,
                model_provider=provider.name
            )
            db.add(assistant_msg)
            await db.commit()
        except Exception as e:
            logger.error(f"Error saving assistant message: {e}")

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
