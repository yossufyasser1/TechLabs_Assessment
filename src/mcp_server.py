"""
MCP (Model Context Protocol) Server implementation for TechLabs Assessment.

This script exposes our core note storage tools as an MCP server.
Any MCP-compatible client (like Claude Desktop, Cursor, or other agents) 
can connect to this server over stdio and natively use the tools.
"""

from mcp.server.fastmcp import FastMCP

# Import our existing database and core execution logic
from src.storage.database import NoteDatabase
from src.tools.note_tools import (
    execute_create_note, execute_list_notes, execute_get_note, 
    execute_update_note, execute_delete_note
)
from src.config import DB_PATH

# Create the MCP Server instance
mcp = FastMCP("TechLabs_Note_Agent")
MCP_USER_ID = "mcp_client_user"

def get_db():
    return NoteDatabase(DB_PATH)

# Using FastMCP decorators to seamlessly expose our tools to any MCP Client
@mcp.tool()
def create_note(title: str, body: str, tags: list[str] = None) -> str:
    """Create a new note. Use this when the user wants to save or record something."""
    with get_db() as db:
        return execute_create_note(db, MCP_USER_ID, title, body, tags or [])

@mcp.tool()
def list_notes(tag: str = None, keyword: str = None, semantic_query: str = None, date_from: str = None, date_to: str = None) -> str:
    """List or search notes using filters. Always use this to find notes before attempting updates/deletes."""
    with get_db() as db:
        return execute_list_notes(db, MCP_USER_ID, tag, keyword, date_from, date_to, semantic_query)

@mcp.tool()
def get_note(note_id: str) -> str:
    """Retrieve exactly one note by its UUID."""
    with get_db() as db:
        return execute_get_note(db, MCP_USER_ID, note_id)

@mcp.tool()
def update_note(note_id: str, title: str = None, body: str = None, tags: list[str] = None) -> str:
    """Modify an existing note. YOU MUST call list_notes first to verify the note_id exists."""
    with get_db() as db:
        return execute_update_note(db, MCP_USER_ID, note_id, title, body, tags)

@mcp.tool()
def delete_note(note_id: str) -> str:
    """Permanently delete a note. YOU MUST call list_notes first to verify the note_id exists."""
    with get_db() as db:
        return execute_delete_note(db, MCP_USER_ID, note_id)

if __name__ == "__main__":
    mcp.run(transport='stdio')
