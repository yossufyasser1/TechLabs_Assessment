"""Unit tests for the tool logic implementations."""

import json
from src.tools.note_tools import (
    execute_create_note, execute_list_notes, 
    execute_get_note, execute_update_note, execute_delete_note
)

def test_create_tool(temp_db):
    res_str = execute_create_note(temp_db, "user1", "T", "B", ["tag"])
    res = json.loads(res_str)
    assert res["title"] == "T"
    assert res["tags"] == ["tag"]
    
def test_list_tools(temp_db):
    execute_create_note(temp_db, "user1", "T1", "B1", ["tag"])
    
    # Positive search
    res_str = execute_list_notes(temp_db, "user1", tag="tag")
    res = json.loads(res_str)
    assert len(res) == 1
    assert res[0]["title"] == "T1"
    
    # Negative search
    res_str2 = execute_list_notes(temp_db, "user1", tag="missing")
    res2 = json.loads(res_str2)
    assert "results" in res2
    assert len(res2["results"]) == 0
    assert "message" in res2 # Verifying graceful error handling rule

def test_delete_tool(temp_db):
    note_str = execute_create_note(temp_db, "user1", "T", "B", [])
    note_id = json.loads(note_str)["id"]
    
    del_str = execute_delete_note(temp_db, note_id)
    del_res = json.loads(del_str)
    assert del_res["deleted"] is True
    
    # Verify gracefully handling delete of missing note
    del_str2 = execute_delete_note(temp_db, "bad_id")
    del_res2 = json.loads(del_str2)
    assert "error" in del_res2
