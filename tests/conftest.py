"""
Pytest fixtures shared across all test files.
Ensures we use a temporary SQLite database for testing to avoid wiping real notes.
"""
import pytest
import tempfile
from pathlib import Path
from src.storage.database import NoteDatabase

@pytest.fixture
def temp_db():
    """Provides a fresh NoteDatabase instance mapped to a temporary file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = str(Path(temp_dir) / "test_notes.db")
        with NoteDatabase(db_path) as db:
            yield db
