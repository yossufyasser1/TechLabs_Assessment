"""Unit tests for the NoteDatabase SQLite wrapper."""

def test_database_creation(temp_db):
    note = temp_db.create("Test Title", "Test Body", ["test", "tag"], "user1")
    
    assert note.id is not None
    assert note.title == "Test Title"
    assert note.body == "Test Body"
    assert note.tags == ["test", "tag"]
    assert note.user_id == "user1"

def test_database_get(temp_db):
    note = temp_db.create("A", "B", [], "u1")
    retrieved = temp_db.get(note.id)
    assert retrieved.title == "A"
    
def test_database_list_filter(temp_db):
    temp_db.create("T1", "B1", ["urgent"], "u1")
    temp_db.create("T2", "B2", ["personal"], "u1")
    temp_db.create("T3", "B3", ["urgent"], "u2")  # Different user
    
    # Filter by user
    assert len(temp_db.list_notes("u1")) == 2
    assert len(temp_db.list_notes("u2")) == 1
    
    # Filter by user and tag
    res = temp_db.list_notes("u1", tag="urgent")
    assert len(res) == 1
    assert res[0].title == "T1"

def test_database_fts_keyword(temp_db):
    temp_db.create("Hello World", "This is python", [], "u1")
    temp_db.create("LangGraph", "Graph database tool calls", [], "u1")
    
    res = temp_db.list_notes("u1", keyword="python")
    assert len(res) == 1
    assert res[0].title == "Hello World"

def test_database_update(temp_db):
    note = temp_db.create("A", "B", ["t1"], "u1")
    updated = temp_db.update(note.id, title="New", tags=["t2"])
    
    assert updated.title == "New"
    assert updated.body == "B"  # unchanged
    assert updated.tags == ["t2"] # completely replaced

def test_database_delete(temp_db):
    note = temp_db.create("A", "B", [], "u1")
    assert temp_db.get(note.id) is not None
    
    res = temp_db.delete(note.id)
    assert res is True
    assert temp_db.get(note.id) is None
