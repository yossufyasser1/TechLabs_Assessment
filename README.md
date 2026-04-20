# Note Agent

A conversational note-taking agent that lets you manage personal notes through natural language. Built with Python and Anthropic's Claude.

## Quick Start

```bash
# 1. Clone and install
git clone <repo-url>
cd note-agent
pip install -e ".[dev]"

# 2. Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Run
python -m src.main
```

**With Docker:**
```bash
cp .env.example .env
# Edit .env with your API key
docker compose up --build
```

## What It Does

Talk to the agent in plain English to manage your notes:

```
You: Save a note about the team standup — we agreed to move it to Tuesdays, tag it as meetings
Agent: Done — saved "Team Standup" with tag [meetings].

You: What did I write about meetings?
Agent: You have 1 note tagged "meetings": Team Standup — you agreed to move it to Tuesdays.

You: Update that note to say the meeting is now on Wednesdays
Agent: Updated — the body now says the meeting is on Wednesdays.

You: Delete it
Agent: Are you sure you want to delete "Team Standup"?

You: Yes
Agent: Done — deleted "Team Standup".
```

### Core Capabilities

- **Add notes** — with title, body, and optional tags
- **List & search** — by keyword (FTS5), tag, date, or semantic similarity
- **Modify notes** — update title, body, or tags
- **Delete notes** — with confirmation before destructive actions
- **Answer questions** — summarise, compare, or reason over your notes

### Behaviours

- **Disambiguation**: If multiple notes match, the agent asks which one you mean
- **Confirmation**: Asks before deleting or making major changes
- **Multi-turn awareness**: Understands "that note" and "the last one" from context
- **Graceful errors**: Clear messages when searches return nothing

## Architecture

```
User → CLI (Rich) → Agent → Claude API (tool-calling) → Tools → SQLite
                      ↑                                     ↓
                      └──────── tool results ───────────────┘
```

The agent follows a simple loop:
1. Send conversation history + tool schemas to Claude
2. If Claude calls a tool → execute it, send the result back
3. Repeat until Claude responds with text

**6 tools**: `create_note`, `list_notes`, `search_notes_semantic`, `get_note`, `update_note`, `delete_note`

See [docs/tool_schemas.md](docs/tool_schemas.md) for full schema documentation.

## Design Decisions

### Why SQLite (not a JSON file)?
- ACID-compliant — no data corruption from crashes
- Built-in FTS5 for full-text search — no extra dependencies
- SQL queries for filtering by tag, date, keyword
- A JSON file would need manual locking and linear scans

### Why no `summarise_notes` tool?
Summarisation is the LLM's job, not a tool's. Tools do things the LLM can't (read from a DB, call an API). The agent calls `list_notes` / `search_notes`, gets the raw notes, and summarises them natively in its response. Cleaner architecture, fewer tokens.

### Why confirmation via system prompt (not a tool parameter)?
A `confirmed: bool` parameter on `delete_note` is fragile — nothing stops the LLM from passing `true` on the first call. The system prompt instructs the agent to ask for confirmation in natural language before calling the tool at all. Simpler, more reliable.

### Why no conversation history summarisation?
Sliding-window summarisation sounds good but risks losing specific note IDs or earlier context, breaking multi-turn tests. For this scope, conversations don't get long enough to need it. Documented as a production TODO.

## Semantic Search (Optional)

If you set `OPENAI_API_KEY` in your `.env`, the agent enables semantic similarity search using OpenAI's `text-embedding-3-small` model.

```bash
# .env
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key  # optional, for semantic search
```

**Why `text-embedding-3-small`?** Cheapest OpenAI embedding model, good quality for this scale. Embeddings are stored as JSON in a SQLite column and cosine similarity is computed in pure Python — no numpy or vector database needed.

**Without an OpenAI key**, the agent falls back to FTS5 keyword search.

```bash
pip install "note-agent[semantic]"  # installs the openai package
```

## MCP Server (Optional)

Exposes note tools via the [Model Context Protocol](https://modelcontextprotocol.io/) for any MCP-compatible client:

```bash
pip install "note-agent[mcp]"
python -m src.mcp_server
```

## Multi-User Support

Notes are scoped by user ID. Pass `--user` to isolate notes:

```bash
python -m src.main --user alice
python -m src.main --user bob
```

Each user only sees their own notes. In production, this would be backed by proper authentication; here the user ID is a trusted CLI argument.

## Testing

### Unit Tests (no API key needed)
```bash
pytest tests/test_database.py tests/test_tools.py -v
```

### Evaluation Harness (needs ANTHROPIC_API_KEY)
```bash
python -m tests.eval.harness
```

Runs 15 conversational scenarios (8 happy path + 7 edge cases) through the real agent, checking both response content and database state. See [tests/eval/scenarios.py](tests/eval/scenarios.py) for the full list.

## Project Structure

```
src/
├── main.py          # CLI entry point
├── agent.py         # Agent loop + system prompt
├── tools.py         # Tool schemas + implementations
├── database.py      # SQLite storage + FTS5
├── embeddings.py    # Optional semantic search
├── models.py        # Note dataclass
├── config.py        # Environment config
└── mcp_server.py    # MCP server (bonus)
tests/
├── test_database.py # Storage layer tests
├── test_tools.py    # Tool dispatch tests
└── eval/
    ├── scenarios.py # 15 test scenarios
    └── harness.py   # Evaluation runner
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | — | Anthropic API key for Claude |
| `MODEL_NAME` | No | `claude-sonnet-4-20250514` | Model to use |
| `DB_PATH` | No | `data/notes.db` | SQLite database file path |
| `OPENAI_API_KEY` | No | — | Enables semantic search if set |
