import os
import sys
import re
import json
import asyncio
from pathlib import Path

# Add backend directory to sys.path so we can import app modules
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, delete
from app.config import settings
from app.models.db_models import TranscriptChunk, Base
from app.rag.embeddings import get_embedding
from app.database import init_db, IS_SQLITE_MODE

DATA_DIR = BACKEND_DIR / "data" / "seed_transcripts"
CLONED_DIR = BACKEND_DIR / "data" / "cloned_transcripts"

def parse_transcript_metadata(content: str, filename: str):
    """Extract guest name, episode title, and topic from transcript markdown header."""
    lines = content.split("\n")
    title = filename.replace(".md", "").replace("_", " ").title()
    guest = "Lenny's Guest"
    topic = "Product & Growth"

    for line in lines[:15]:
        if line.startswith("# "):
            title = line[2:].strip()
        elif "**Guest:**" in line:
            guest = line.split("**Guest:**")[1].strip()
        elif "**Topic:**" in line:
            topic = line.split("**Topic:**")[1].strip()

    return title, guest, topic

def chunk_text(text_content: str, chunk_size: int = 1500, overlap: int = 250):
    """
    Split transcript text into overlapping chunks with section preservation.
    """
    # Split on markdown section headers or double newlines
    sections = re.split(r'\n(?=## )', text_content)
    chunks = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract timestamp if present in the section (e.g. [Timestamp: 12:40])
        ts_match = re.search(r'\[Timestamp:\s*([^\]]+)\]', section)
        timestamp_ref = ts_match.group(1) if ts_match else "Overview"

        if len(section) <= chunk_size:
            chunks.append((section, timestamp_ref))
        else:
            # Sub-chunk with overlap
            start = 0
            while start < len(section):
                end = min(start + chunk_size, len(section))
                sub_chunk = section[start:end]
                chunks.append((sub_chunk, timestamp_ref))
                start += chunk_size - overlap

    return chunks

async def ingest_transcripts():
    print("=" * 60)
    print("[*] Starting Lenny's Podcast Transcript Ingestion...")
    print("=" * 60)

    await init_db()
    from app.database import get_session_factory
    AsyncSessionLocal = get_session_factory()

    all_files = []
    if DATA_DIR.exists():
        all_files.extend(list(DATA_DIR.glob("*.md")))
    if CLONED_DIR.exists():
        all_files.extend(list(CLONED_DIR.glob("**/*.md")))

    print(f"[*] Found {len(all_files)} transcript files to process.")

    total_chunks = 0
    async with AsyncSessionLocal() as session:
        # Clear existing chunks to avoid duplicates
        await session.execute(delete(TranscriptChunk))
        await session.commit()

        for file_path in all_files:
            print(f"[*] Ingesting: {file_path.name}")
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            title, guest, topic = parse_transcript_metadata(content, file_path.name)
            chunks = chunk_text(content)

            for chunk_str, ts_ref in chunks:
                if len(chunk_str.strip()) < 50:
                    continue

                # Prepend metadata context header
                formatted_chunk = f"[{title} | Guest: {guest} | Timestamp: {ts_ref}]\n{chunk_str}"
                embedding = get_embedding(formatted_chunk)

                db_chunk = TranscriptChunk(
                    episode_title=title,
                    guest_name=guest,
                    episode_url=f"https://www.lennyspodcast.com/search?q={guest.replace(' ', '+')}",
                    timestamp_ref=ts_ref,
                    chunk_text=formatted_chunk,
                    embedding_json=json.dumps(embedding)
                )
                session.add(db_chunk)
                total_chunks += 1

        await session.commit()

    print("=" * 60)
    print(f"[+] Ingestion complete! Successfully indexed {total_chunks} chunks from {len(all_files)} episodes.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(ingest_transcripts())
