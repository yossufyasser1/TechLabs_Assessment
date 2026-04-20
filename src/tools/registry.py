"""
Bundles the schemas and execution logic into LangChain @tool objects.
The Agent Graph will import `AGENT_TOOLS` from here.
"""
from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig

from src.storage.database import NoteDatabase
from src.tools.schemas import (
    CreateNoteSchema, ListNotesSchema, GetNoteSchema, 
    UpdateNoteSchema, DeleteNoteSchema
)
from src.tools.note_tools import (
    execute_create_note, execute_list_notes, execute_get_note, 
    execute_update_note, execute_delete_note
)

@tool(args_schema=CreateNoteSchema)
def create_note_tool(title: str, body: str, tags: list[str] = None, config: RunnableConfig = None) -> str:
    """Create a new note. Use this when the user wants to save or record something."""
    db: NoteDatabase = config.get("configurable", {}).get("db")
    user_id: str = config.get("configurable", {}).get("user_id", "default")
    return execute_create_note(db, user_id, title, body, tags or [])

@tool(args_schema=ListNotesSchema)
def list_notes_tool(tag: str = None, keyword: str = None, date_from: str = None, date_to: str = None, config: RunnableConfig = None) -> str:
    """List or search notes using filters. Always use this to find notes before attempting updates/deletes."""
    db: NoteDatabase = config.get("configurable", {}).get("db")
    user_id: str = config.get("configurable", {}).get("user_id", "default")
    return execute_list_notes(db, user_id, tag, keyword, date_from, date_to)

@tool(args_schema=GetNoteSchema)
def get_note_tool(note_id: str, config: RunnableConfig = None) -> str:
    """Retrieve exactly one note by its UUID."""
    db: NoteDatabase = config.get("configurable", {}).get("db")
    return execute_get_note(db, note_id)

@tool(args_schema=UpdateNoteSchema)
def update_note_tool(note_id: str, title: str = None, body: str = None, tags: list[str] = None, config: RunnableConfig = None) -> str:
    """Modify an existing note. Only provided fields change."""
    db: NoteDatabase = config.get("configurable", {}).get("db")
    return execute_update_note(db, note_id, title, body, tags)

@tool(args_schema=DeleteNoteSchema)
def delete_note_tool(note_id: str, config: RunnableConfig = None) -> str:
    """Permanently delete a note. Requires explicit user confirmation first."""
    db: NoteDatabase = config.get("configurable", {}).get("db")
    return execute_delete_note(db, note_id)

# The exported registry of tools ready for the LLM
AGENT_TOOLS = [
    create_note_tool,
    list_notes_tool,
    get_note_tool,
    update_note_tool,
    delete_note_tool
]
