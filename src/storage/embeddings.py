"""
Optional semantic search using OpenAI embeddings stored in SQLite.

Embeds note text with text-embedding-3-small and computes cosine
similarity in pure Python.
"""

import math
import os
from typing import Optional

from .database import NoteDatabase

_client = None


def _get_client():
    global _client
    if _client is None:
        try:
            from openai import OpenAI

            _client = OpenAI()
        except (ImportError, Exception):
            return None
    return _client


def is_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY")) and _get_client() is not None


def get_embedding(text: str) -> Optional[list[float]]:
    client = _get_client()
    if not client:
        return None

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def embed_note(db: NoteDatabase, note_id: str, title: str, body: str, tags: list[str]):
    text = f"{title}\n{body}\n{' '.join(tags)}"
    embedding = get_embedding(text)
    if embedding is not None:
        db.save_embedding(note_id, embedding)


def search_similar(
    db: NoteDatabase, query: str, user_id: str, top_k: int = 5
) -> list[tuple[str, float]]:
    query_embedding = get_embedding(query)
    if query_embedding is None:
        return []

    all_embeddings = db.get_all_embeddings(user_id)

    scored = []
    for note_id, note_embedding in all_embeddings:
        score = cosine_similarity(query_embedding, note_embedding)
        scored.append((note_id, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]