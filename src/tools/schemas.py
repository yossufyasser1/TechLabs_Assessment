"""
Pydantic schemas explicitly defining the data models for our agent's tools.
This demonstrates clean, well-typed tool interfaces for the evaluation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class CreateNoteSchema(BaseModel):
    title: str = Field(description="A short, descriptive title for the note")
    body: str = Field(description="The main text content of the note")
    tags: Optional[List[str]] = Field(default_factory=list, description="Optional categories for the note (e.g. ['meetings', 'urgent'])")

class ListNotesSchema(BaseModel):
    tag: Optional[str] = Field(None, description="Filter notes by an exact tag match")
    keyword: Optional[str] = Field(None, description="Full-text exact keyword phrase to look for inside titles and bodies")
    semantic_query: Optional[str] = Field(None, description="Search notes by their underlying meaning or intent (semantic search via Ollama embeddings)")
    date_from: Optional[str] = Field(None, description="Show notes created on or after this date (ISO 8601 format)")
    date_to: Optional[str] = Field(None, description="Show notes created on or before this date (ISO 8601 format)")

class GetNoteSchema(BaseModel):
    note_id: str = Field(description="The UUID of the note to retrieve")

class UpdateNoteSchema(BaseModel):
    note_id: str = Field(description="The UUID of the note to modify")
    title: Optional[str] = Field(None, description="A new title for the note (omit if not changing)")
    body: Optional[str] = Field(None, description="New body text content (omit if not changing)")
    tags: Optional[List[str]] = Field(None, description="New collection of tags (replaces old tags completely, omit if not changing)")

class DeleteNoteSchema(BaseModel):
    note_id: str = Field(description="The UUID of the note to permanently delete")
