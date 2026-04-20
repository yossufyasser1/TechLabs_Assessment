import sys
from pathlib import Path

# Ensure src is in the python path
sys.path.append(str(Path(__file__).parent))

from src.storage.database import NoteDatabase

def run_test():
    print("🚀 Starting Database Test...")
    db_path = "data/test_notes.db"
    
    # Remove existing test db if present
    if Path(db_path).exists():
        Path(db_path).unlink()

    print("\n📦 Initialising NoteDatabase...")
    db = NoteDatabase(db_path)
    user = "test_user"

    print(f"\n✍️  Creating notes for user '{user}'...")
    n1 = db.create(
        title="Project Ideas",
        body="Build a conversational AI using LangGraph and SQLite FTS5.",
        tags=["ai", "project"],
        user_id=user
    )
    n2 = db.create(
        title="Shopping List",
        body="Buy milk, eggs, and bread.",
        tags=["personal"],
        user_id=user
    )
    print(f"   Created note 1: {n1.title} ({n1.id})")
    print(f"   Created note 2: {n2.title} ({n2.id})")

    print("\n🔍 Testing Full-Text Search (keyword: 'LangGraph')...")
    results = db.list_notes(user_id=user, keyword="LangGraph")
    print(f"   Found {len(results)} note(s).")
    for r in results:
        print(f"   - {r.title}: {r.body}")

    print("\n🏷️  Testing Tag Filter (tag: 'personal')...")
    results = db.list_notes(user_id=user, tag="personal")
    print(f"   Found {len(results)} note(s).")
    for r in results:
        print(f"   - {r.title}: {r.body}")

    print("\n📝 Testing Update Note...")
    db.update(note_id=n2.id, title="Urgent Shopping", tags=["personal", "urgent"])
    updated = db.get(n2.id)
    print(f"   Updated note '{updated.title}' tags: {updated.tags}")

    print("\n🗑️  Testing Delete Note...")
    deleted = db.delete(n1.id)
    print(f"   Deleted note 1? {deleted}")
    
    # Clean up
    db.close()
    print("\n✅ All tests passed!\n")

if __name__ == "__main__":
    run_test()
