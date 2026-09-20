import json
import logging
import numpy as np
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.rag.embeddings import get_embedding
from app.models.db_models import TranscriptChunk
import app.database as db_module
from app.config import settings

logger = logging.getLogger(__name__)

class TranscriptRetriever:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 4,
        similarity_threshold: float = 0.45
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top-K relevant chunks with cosine similarity >= threshold.
        Supports PostgreSQL pgvector syntax when active, and in-memory cosine comparison for SQLite.
        """
        query_vec = np.array(get_embedding(query), dtype=np.float32)
        
        # 1. Check if we have pgvector in PostgreSQL
        is_sqlite = db_module.IS_SQLITE_MODE or (self.db.bind and "sqlite" in str(self.db.bind.url))
        if not is_sqlite:
            try:
                # pgvector cosine similarity: 1 - (embedding <=> :vector::vector)
                query_stmt = text("""
                    SELECT
                        episode_title,
                        guest_name,
                        episode_url,
                        timestamp_ref,
                        chunk_text,
                        1 - (embedding <=> :vector::vector) AS similarity_score
                    FROM transcript_chunks
                    WHERE 1 - (embedding <=> :vector::vector) >= :threshold
                    ORDER BY similarity_score DESC
                    LIMIT :limit;
                """)
                result = await self.db.execute(
                    query_stmt,
                    {
                        "vector": str(query_vec.tolist()),
                        "threshold": similarity_threshold,
                        "limit": top_k
                    }
                )
                rows = result.fetchall()
                if rows:
                    return [
                        {
                            "episode": r.episode_title,
                            "guest": r.guest_name,
                            "timestamp": r.timestamp_ref or "General",
                            "text": r.chunk_text,
                            "score": round(float(r.similarity_score), 3),
                            "url": r.episode_url
                        }
                        for r in rows
                    ]
            except Exception as e:
                logger.warning(f"PostgreSQL pgvector query failed ({e}). Falling back to row scan.")

        # 2. SQLite / Generic SQLAlchemy query fallback
        stmt = select(TranscriptChunk)
        result = await self.db.execute(stmt)
        chunks = result.scalars().all()
        
        if not chunks:
            return []

        scored_chunks = []
        for c in chunks:
            try:
                chunk_vec = np.array(json.loads(c.embedding_json), dtype=np.float32)
                # Cosine similarity between normalized vectors = dot product
                norm_q = np.linalg.norm(query_vec)
                norm_c = np.linalg.norm(chunk_vec)
                if norm_q > 0 and norm_c > 0:
                    sim = float(np.dot(query_vec, chunk_vec) / (norm_q * norm_c))
                else:
                    sim = 0.0

                if sim >= similarity_threshold:
                    scored_chunks.append({
                        "episode": c.episode_title,
                        "guest": c.guest_name,
                        "timestamp": c.timestamp_ref or "General",
                        "text": c.chunk_text,
                        "score": round(sim, 3),
                        "url": c.episode_url
                    })
            except Exception:
                continue

        # Sort descending by similarity score
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    @staticmethod
    def format_grounded_context(chunks: List[Dict[str, Any]]) -> str:
        """Formats retrieved chunks into grounded system context."""
        if not chunks:
            return "No relevant transcripts found in Lenny's podcast archive."

        sections = []
        for i, c in enumerate(chunks, 1):
            sections.append(
                f"[Source {i}] Episode: '{c['episode']}' | Guest: {c['guest']} | Timestamp/Section: {c['timestamp']}\n"
                f"{c['text']}"
            )
        return "\n\n---\n\n".join(sections)
