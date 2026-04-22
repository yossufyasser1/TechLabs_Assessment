"""
Semantic search using embeddings stored in SQLite.

By default uses local Ollama Embeddings, but can fallback
to OpenAI embeddings if configured in the environment.
"""

import math
from typing import Optional

from src.config import LLM_PROVIDER, OPENAI_API_KEY
from .database import NoteDatabase

_embedder = None

def _get_embedder():
    global _embedder
    if _embedder is None:
        try:
            if LLM_PROVIDER == "openai":
                from langchain_openai import OpenAIEmbeddings
                _embedder = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
            else:
                from langchain_ollama import OllamaEmbeddings
                _embedder = OllamaEmbeddings(model="llama3.1")
        except Exception:
            return None
    return _embedder

def is_available() -> bool:
    return _get_embedder() is not None

def get_embedding(text: str) -> Optional[list[float]]:
    embedder = _get_embedder()
    if not embedder:
        return None
    try:
        return embedder.embed_query(text)
    except Exception:
        return None

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