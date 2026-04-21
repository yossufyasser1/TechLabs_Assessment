"""
SQLite storage for notes with full-text search.

Why SQLite:
- Zero-config, single-file, ACID-compliant
- Built-in FTS5 for full-text search — no extra dependencies
- Perfect for this scale; a JSON file would lack efficient querying
  and concurrent access safety

The FTS5 index is kept in sync via triggers, so inserts/updates/deletes
on the notes table automatically update the search index.
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .models import Note


def _row_to_note(row: sqlite3.Row) -> Note:
    """Convert a database row into a Note object."""
    return Note(
        id=row["id"],
        title=row["title"],
        body=row["body"],
        tags=json.loads(row["tags"]),
        user_id=row["user_id"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


class NoteDatabase:
    """Manages note persistence and full-text search in SQLite."""

    def __init__(self, db_path: str = "data/notes.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _create_tables(self):
        """Create the schema and FTS triggers if they don't exist yet."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                tags TEXT NOT NULL DEFAULT '[]',
                user_id TEXT NOT NULL DEFAULT 'default',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                embedding TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);
        """)

        has_fts = self.conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='notes_fts'"
        ).fetchone()

        if not has_fts:
            self.conn.executescript("""
                CREATE VIRTUAL TABLE notes_fts USING fts5(
                    title, body, tags,
                    content='notes', content_rowid='rowid'
                );

                CREATE TRIGGER notes_fts_insert AFTER INSERT ON notes BEGIN
                    INSERT INTO notes_fts(rowid, title, body, tags)
                    VALUES (new.rowid, new.title, new.body, new.tags);
                END;

                CREATE TRIGGER notes_fts_delete AFTER DELETE ON notes BEGIN
                    INSERT INTO notes_fts(notes_fts, rowid, title, body, tags)
                    VALUES ('delete', old.rowid, old.title, old.body, old.tags);
                END;

                CREATE TRIGGER notes_fts_update AFTER UPDATE ON notes BEGIN
                    INSERT INTO notes_fts(notes_fts, rowid, title, body, tags)
                    VALUES ('delete', old.rowid, old.title, old.body, old.tags);
                    INSERT INTO notes_fts(rowid, title, body, tags)
                    VALUES (new.rowid, new.title, new.body, new.tags);
                END;
            """)

        self.conn.commit()

    def create(self, title: str, body: str, tags: list[str], user_id: str) -> Note:
        """Create a new note. Returns the created Note."""
        note_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        self.conn.execute(
            """INSERT INTO notes (id, title, body, tags, user_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (note_id, title, body, json.dumps(tags), user_id, now, now),
        )
        self.conn.commit()
        return self.get(note_id, user_id)

    def get(self, note_id: str, user_id: str) -> Optional[Note]:
        """Get a note by ID for a specific user."""
        row = self.conn.execute(
            "SELECT * FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id)
        ).fetchone()
        return _row_to_note(row) if row else None

    def list_notes(
        self,
        user_id: str,
        tag: Optional[str] = None,
        keyword: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[Note]:
        if keyword:
            # Escape quotes to avoid FTS5 syntax errors and use wildcard matching
            safe_kw = keyword.replace('"', '')
            fts_query = f'"{safe_kw}"*'
            query = """
                SELECT notes.* FROM notes
                JOIN notes_fts ON notes.rowid = notes_fts.rowid
                WHERE notes.user_id = ? AND notes_fts MATCH ?
            """
            params: list = [user_id, fts_query]
        else:
            query = "SELECT * FROM notes WHERE user_id = ?"
            params = [user_id]

        if tag:
            query += " AND notes.tags LIKE ?"
            params.append(f'%"{tag}"%')

        if date_from:
            query += " AND notes.created_at >= ?"
            params.append(date_from)

        if date_to:
            query += " AND notes.created_at <= ?"
            params.append(date_to)

        query += " ORDER BY notes.updated_at DESC"

        try:
            rows = self.conn.execute(query, params).fetchall()
            return [_row_to_note(r) for r in rows]
        except sqlite3.OperationalError:
            # Fallback if FTS5 query causes unexpected syntax error
            return []

    def update(
        self,
        user_id: str,
        note_id: str,
        title: Optional[str] = None,
        body: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> Optional[Note]:
        note = self.get(note_id, user_id)
        if not note:
            return None

        new_title = title if title is not None else note.title
        new_body = body if body is not None else note.body
        new_tags = json.dumps(tags if tags is not None else note.tags)
        now = datetime.now(timezone.utc).isoformat()

        self.conn.execute(
            "UPDATE notes SET title=?, body=?, tags=?, updated_at=? WHERE id=? AND user_id=?",
            (new_title, new_body, new_tags, now, note_id, user_id),
        )
        self.conn.commit()
        return self.get(note_id, user_id)

    def delete(self, note_id: str, user_id: str) -> bool:
        cursor = self.conn.execute(
            "DELETE FROM notes WHERE id = ? AND user_id = ?",
            (note_id, user_id),
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def save_embedding(self, note_id: str, embedding: list[float]):
        self.conn.execute(
            "UPDATE notes SET embedding = ? WHERE id = ?",
            (json.dumps(embedding), note_id),
        )
        self.conn.commit()

    def get_all_embeddings(self, user_id: str) -> list[tuple[str, list[float]]]:
        rows = self.conn.execute(
            "SELECT id, embedding FROM notes WHERE user_id = ? AND embedding IS NOT NULL",
            (user_id,),
        ).fetchall()
        return [(row["id"], json.loads(row["embedding"])) for row in rows]

    def close(self):
        self.conn.close()