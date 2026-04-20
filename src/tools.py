"""
Tool definitions using LangChain's @tool decorator.

Notice how we completely removed the massive JSON schemas!
LangChain reads the Python type hints and the docstrings, and automatically
translates them on-the-fly into whatever format the LLM needs (Gemini, OpenAI, Claude).
This makes our tools 100% model-agnostic.
"""

import json
from typing import Optional, List
from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig

from src.storage.database import NoteDatabase


@tool
def create_note(title: str, body: str, tags: Optional[List[str]] = None, config: RunnableConfig = None) -> str:
    """
    Create a new note. Use this when the user wants to save, record, or jot something down.
    
    Args:
        title: A short, descriptive title for the note.
        body: The main content of the note.
        tags: Optional tags or categories (e.g. ['meetings', 'urgent']).
    """
    db: NoteDatabase = config.get("configurable", {}).get("db")
    user_id: str = config.get("configurable", {}).get("user_id", "default")
    
    tags = tags or []
    note = db.create(title, body, tags, user_id)
    return json.dumps(note.to_dict())


@tool
def list_notes(
    tag: Optional[str] = None, 
    keyword: Optional[str] = None, 
    date_from: Optional[str] = None, 
    date_to: Optional[str] = None,
    config: RunnableConfig = None
) -> str:
    """
    List notes with optional filters. Returns all notes for the user if no filters are provided.
    Use this for keyword searches, filtering by tag, or browsing notes by date range.
    
    Args:
        tag: Filter by tag name (exact match).
        keyword: Full-text search keyword or phrase (searches inside titles and bodies).
        date_from: Show notes created on or after this date (ISO 8601, e.g. 2024-01-15).
        date_to: Show notes created on or before this date (ISO 8601).
    """
    db: NoteDatabase = config.get("configurable", {}).get("db")
    user_id: str = config.get("configurable", {}).get("user_id", "default")
    
    notes = db.list_notes(user_id, tag=tag, keyword=keyword, date_from=date_from, date_to=date_to)
    if not notes:
        return json.dumps({"results": [], "message": "No notes found matching your criteria."})
    return json.dumps([n.to_dict() for n in notes])


@tool
def get_note(note_id: str, config: RunnableConfig = None) -> str:
    """
    Retrieve a specific note by its UUID. Use when you already know which note to fetch.
    """
    db: NoteDatabase = config.get("configurable", {}).get("db")
    note = db.get(note_id)
    if not note:
        return json.dumps({"error": f"No note found with ID {note_id}"})
    return json.dumps(note.to_dict())


@tool
def update_note(
    note_id: str, 
    title: Optional[str] = None, 
    body: Optional[str] = None, 
    tags: Optional[List[str]] = None,
    config: RunnableConfig = None
) -> str:
    """
    Update an existing note. Only the fields you provide will be changed; omitted fields keep their current values.
    
    Args:
        note_id: The UUID of the note to update.
        title: New title (omit to keep current).
        body: New body text (omit to keep current).
        tags: New tags (replaces all existing tags, omit to keep current).
    """
    db: NoteDatabase = config.get("configurable", {}).get("db")
    note = db.update(note_id, title=title, body=body, tags=tags)
    if not note:
        return json.dumps({"error": f"No note found with ID {note_id}"})
    return json.dumps(note.to_dict())


@tool
def delete_note(note_id: str, config: RunnableConfig = None) -> str:
    """
    Permanently delete a note. This cannot be undone. 
    Always confirm with the user before calling this.
    """
    db: NoteDatabase = config.get("configurable", {}).get("db")
    note = db.get(note_id)
    if not note:
        return json.dumps({"error": f"No note found with ID {note_id}"})

    db.delete(note_id)
    return json.dumps({"deleted": True, "title": note.title})

# List of tools to pass into the LangGraph Agent
AGENT_TOOLS = [create_note, list_notes, get_note, update_note, delete_note]
