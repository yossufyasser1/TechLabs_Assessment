# Tool Schema Documentation

This document describes every tool the agent can call, its input parameters, and its return format. All schemas are enforced via Pydantic at runtime.

---

## `create_note_tool`
**Purpose:** Create a new note in the database.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `title` | `str` | ✅ | Short, descriptive title |
| `body` | `str` | ✅ | Main text content |
| `tags` | `list[str]` | ❌ | Optional category labels (e.g. `["meetings", "urgent"]`) |

**Returns:** JSON object of the created note including its auto-generated `id`, `created_at`, and `updated_at`.

---

## `list_notes_tool`
**Purpose:** List or search notes. Supports filtering by tag, keyword, and date range. Always call this before update/delete to retrieve a valid `note_id`.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `tag` | `str` | ❌ | Filter by exact tag match |
| `keyword` | `str` | ❌ | Full-text search across title and body (uses FTS5) |
| `date_from` | `str` | ❌ | ISO 8601 date — return notes created on or after this date |
| `date_to` | `str` | ❌ | ISO 8601 date — return notes created on or before this date |

**Returns:** JSON array of matching notes, or `{"results": [], "message": "No notes found..."}` when empty.

---

## `get_note_tool`
**Purpose:** Fetch a single note by its UUID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `note_id` | `str` | ✅ | UUID of the target note |

**Returns:** JSON object of the note, or `{"error": "Note <id> not found. ..."}`.

---

## `update_note_tool`
**Purpose:** Modify an existing note. Only the fields you provide will change. **Must call `list_notes_tool` first to obtain a valid `note_id`.**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `note_id` | `str` | ✅ | UUID of the note to modify |
| `title` | `str` | ❌ | New title (omit to keep existing) |
| `body` | `str` | ❌ | New body text (omit to keep existing) |
| `tags` | `list[str]` | ❌ | Replacement tag list — **replaces all existing tags** (omit to keep existing) |

**Returns:** JSON object of the updated note, or `{"error": "Note <id> not found. ..."}`.

---

## `delete_note_tool`
**Purpose:** Permanently delete a note. **Must call `list_notes_tool` first to confirm the `note_id` exists, then get explicit user confirmation before calling this tool.**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `note_id` | `str` | ✅ | UUID of the note to delete |

**Returns:** `{"deleted": true, "title": "<note title>"}` on success, or `{"error": "Note <id> not found. ..."}`.

---

## Notes on All Tools

- All tools are **user-scoped** — the `user_id` is injected server-side from the session config and is never passed by the LLM, preventing cross-user data access.
- All tools open and close their own SQLite connection per call (thread-safe for LangGraph's multi-threaded `ToolNode`).
- Error responses include an instruction string directing the agent to call `list_notes_tool` as a self-healing mechanism.
