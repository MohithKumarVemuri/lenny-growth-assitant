import os
import math
import re
import zlib
import numpy as np
from typing import List

# Dimension matches all-MiniLM-L6-v2 standard (384)
EMBEDDING_DIM = 384

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
    "of", "with", "by", "from", "up", "about", "into", "over", "after", 
    "is", "are", "was", "were", "be", "been", "being", "have", "has", 
    "had", "do", "does", "did", "what", "which", "who", "whom", "this", 
    "that", "these", "those", "am", "it", "its", "i", "you", "he", "she", 
    "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", 
    "our", "their", "how", "according"
}

def _deterministic_hash(word: str) -> int:
    return zlib.crc32(word.encode("utf-8"))

def get_embedding(text: str) -> List[float]:
    """
    Generate normalized 384-dim vector embedding.
    Uses fast, deterministic process-independent semantic projection.
    """
    return _semantic_hash_vector(text, EMBEDDING_DIM)

def _semantic_hash_vector(text: str, dim: int = 384) -> List[float]:
    """
    Deterministic word-bag projection with n-gram hashing and unit normalization.
    Uses crc32 for reproducible semantic projection across all processes.
    """
    vec = np.zeros(dim, dtype=np.float32)
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    words = cleaned.split()
    
    if not words:
        return vec.tolist()

    for i, word in enumerate(words):
        weight = 0.2 if word in _STOPWORDS else 1.5
        # 1-gram
        h1 = _deterministic_hash(word) % dim
        vec[h1] += weight
        # 2-gram context
        if i < len(words) - 1:
            next_word = words[i+1]
            bi_weight = 0.3 if (word in _STOPWORDS and next_word in _STOPWORDS) else 2.8
            bi = f"{word}_{next_word}"
            h2 = _deterministic_hash(bi) % dim
            vec[h2] += bi_weight

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()
