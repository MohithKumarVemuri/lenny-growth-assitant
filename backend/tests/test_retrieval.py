import pytest
import pytest_asyncio
import numpy as np
from app.rag.embeddings import get_embedding
from app.rag.retriever import TranscriptRetriever
from app.database import init_db, get_session_factory
from app.models.db_models import TranscriptChunk
import json

@pytest_asyncio.fixture(autouse=True)
async def setup_test_vectors():
    await init_db()
    session_maker = get_session_factory()
    async with session_maker() as session:
        # Seed test chunks
        chunk1 = TranscriptChunk(
            episode_title="Brian Chesky on Founder Mode",
            guest_name="Brian Chesky",
            timestamp_ref="12:40",
            chunk_text="Founder mode means staying in the details and eliminating layers.",
            embedding_json=json.dumps(get_embedding("founder mode brian chesky details airbnb"))
        )
        chunk2 = TranscriptChunk(
            episode_title="Elena Verna on PLG",
            guest_name="Elena Verna",
            timestamp_ref="05:40",
            chunk_text="B2B Product-Led Growth feeds Product-Led Sales through end user adoption.",
            embedding_json=json.dumps(get_embedding("product led growth elena verna plg sales"))
        )
        session.add_all([chunk1, chunk2])
        await session.commit()

@pytest.mark.asyncio
async def test_embedding_dimension():
    vec = get_embedding("Product management growth loop")
    assert len(vec) == 384
    # Check normalized
    norm = np.linalg.norm(vec)
    assert abs(norm - 1.0) < 0.05

@pytest.mark.asyncio
async def test_relevant_chunk_retrieval():
    session_maker = get_session_factory()
    async with session_maker() as session:
        retriever = TranscriptRetriever(session)
        # Search query matching Chesky
        results = await retriever.retrieve_relevant_chunks("What is founder mode according to Brian Chesky?", top_k=2, similarity_threshold=0.3)
        assert len(results) >= 1
        top_match = results[0]
        assert "Founder Mode" in top_match["episode"] or "Brian Chesky" in top_match["guest"]

@pytest.mark.asyncio
async def test_out_of_domain_retrieval_refusal():
    session_maker = get_session_factory()
    async with session_maker() as session:
        retriever = TranscriptRetriever(session)
        # Completely irrelevant query with strict threshold
        results = await retriever.retrieve_relevant_chunks("How do I repair an automobile carburetor engine?", top_k=2, similarity_threshold=0.85)
        # Should return no chunks
        assert len(results) == 0
