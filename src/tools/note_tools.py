"""
Core business logic for note operations.
These functions map the validated inputs to the SQLite database.
"""
import json
from src.storage.database import NoteDatabase

def execute_create_note(db: NoteDatabase, user_id: str, title: str, body: str, tags: list[str]) -> str:
    note = db.create(title, body, tags, user_id)
    return json.dumps(note.to_dict())

def execute_list_notes(db: NoteDatabase, user_id: str, tag: str = None, keyword: str = None, date_from: str = None, date_to: str = None) -> str:
    notes = db.list_notes(user_id, tag=tag, keyword=keyword, date_from=date_from, date_to=date_to)
    if not notes:
        return json.dumps({"results": [], "message": "No notes found matching your criteria."})
    return json.dumps([n.to_dict() for n in notes])

def execute_get_note(db: NoteDatabase, user_id: str, note_id: str) -> str:
    note = db.get(note_id, user_id)
    if not note:
        return json.dumps({"error": f"Note {note_id} not found. You MUST call list_notes_tool to find the correct valid ID."})
    return json.dumps(note.to_dict())

def execute_update_note(db: NoteDatabase, user_id: str, note_id: str, title: str = None, body: str = None, tags: list[str] = None) -> str:
    note = db.update(user_id, note_id, title=title, body=body, tags=tags)
    if not note:
        return json.dumps({"error": f"Note {note_id} not found. You MUST call list_notes_tool to verify valid note IDs before replying."})
    return json.dumps(note.to_dict())

def execute_delete_note(db: NoteDatabase, user_id: str, note_id: str) -> str:
    note = db.get(note_id, user_id)
    if not note:
        return json.dumps({"error": f"Note {note_id} not found. You MUST call list_notes_tool to verify valid note IDs before replying."})
    db.delete(note_id, user_id)
    return json.dumps({"deleted": True, "title": note.title})
