"""
Bundles the schemas and execution logic into LangChain @tool objects.
The Agent Graph will import `AGENT_TOOLS` from here.

Thread-safety note:
    SQLite connections cannot be shared across threads. LangGraph runs
    ToolNode in a different thread from the main graph, so instead of
    passing a `db` object through config, we pass `db_path` and open a
    fresh connection inside each tool call.
"""
from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig

from src.config import DB_PATH
from src.storage.database import NoteDatabase
from src.tools.schemas import (
    CreateNoteSchema, ListNotesSchema, GetNoteSchema, 
    UpdateNoteSchema, DeleteNoteSchema
)
from src.tools.note_tools import (
    execute_create_note, execute_list_notes, execute_get_note, 
    execute_update_note, execute_delete_note
)


def _get_db_and_user(config: RunnableConfig) -> tuple[NoteDatabase, str]:
    """
    Opens a fresh per-thread SQLite connection and extracts user_id.
    Must be called inside each tool so it runs in the correct thread.
    """
    cfg = config.get("configurable", {}) if config else {}
    db_path = cfg.get("db_path", DB_PATH)
    user_id = cfg.get("user_id", "default")
    return NoteDatabase(db_path), user_id


@tool(args_schema=CreateNoteSchema)
def create_note_tool(title: str, body: str, tags: list[str] = None, config: RunnableConfig = None) -> str:
    """Create a new note. Use this when the user wants to save or record something."""
    db, user_id = _get_db_and_user(config)
    try:
        return execute_create_note(db, user_id, title, body, tags or [])
    finally:
        db.close()

@tool(args_schema=ListNotesSchema)
def list_notes_tool(tag: str = None, keyword: str = None, semantic_query: str = None, date_from: str = None, date_to: str = None, config: RunnableConfig = None) -> str:
    """List or search notes using filters. Always use this to find notes before attempting updates/deletes."""
    db, user_id = _get_db_and_user(config)
    try:
        return execute_list_notes(db, user_id, tag, keyword, date_from, date_to, semantic_query)
    finally:
        db.close()

@tool(args_schema=GetNoteSchema)
def get_note_tool(note_id: str, config: RunnableConfig = None) -> str:
    """Retrieve exactly one note by its UUID."""
    db, user_id = _get_db_and_user(config)
    try:
        return execute_get_note(db, user_id, note_id)
    finally:
        db.close()

@tool(args_schema=UpdateNoteSchema)
def update_note_tool(note_id: str, title: str = None, body: str = None, tags: list[str] = None, config: RunnableConfig = None) -> str:
    """Modify an existing note. YOU MUST call list_notes_tool first to verify the note_id exists."""
    db, user_id = _get_db_and_user(config)
    try:
        return execute_update_note(db, user_id, note_id, title, body, tags)
    finally:
        db.close()

@tool(args_schema=DeleteNoteSchema)
def delete_note_tool(note_id: str, config: RunnableConfig = None) -> str:
    """Permanently delete a note. YOU MUST call list_notes_tool first to verify the note_id exists, AND get user confirmation."""
    db, user_id = _get_db_and_user(config)
    try:
        return execute_delete_note(db, user_id, note_id)
    finally:
        db.close()

# The exported registry of tools ready for the LLM
AGENT_TOOLS = [
    create_note_tool,
    list_notes_tool,
    get_note_tool,
    update_note_tool,
    delete_note_tool
]
