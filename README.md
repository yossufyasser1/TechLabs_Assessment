# Conversational Note-Taking Agent

An intelligent command-line chat agent that lets users manage personal notes entirely through natural language — built as part of the **TechLabs London AI Engineer Technical Assessment**.

## ✨ Features

| Feature | Details |
|---|---|
| **Natural Language CRUD** | Create, read, update, delete notes via conversation |
| **Full-Text Search** | SQLite FTS5 for fast keyword & tag-based retrieval |
| **Multi-Turn Awareness** | LangGraph MemorySaver keeps full conversation context |
| **Multi-User Isolation** | Notes scoped per `user_id` at the database level |
| **Destructive Action Guards** | Agent confirms before any delete |
| **Local-First (Privacy)** | Runs 100% offline via Ollama — no cloud API calls |
| **Evaluation Harness** | 15 automated conversational scenarios, pass/fail report |
| **MCP Server** *(Bonus)* | Tools exposed via Model Context Protocol |
| **Semantic Search** *(Bonus)* | Optional cosine similarity on OpenAI embeddings |

---

## ⚙️ Setup

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed and running locally

### 1. Install the model
```bash
ollama pull llama3.1
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
```
The defaults in `.env.example` work out of the box with a local Ollama instance.  
No API keys are needed for core features. (Optional semantic search may require an OpenAI key.)

### 4. Run the agent
```bash
python -m src.main
```
Multi-user support (notes are isolated per user):
```bash
python -m src.main --user alice
```

---

## 🧪 Evaluation Harness

Run the full 15-scenario automated evaluation:
```bash
python -m evals.report
```

Run isolated unit tests:
```bash
pytest tests/
```

---

## 🏗️ Architecture

```
src/
├── agent/
│   ├── agent.py          # LangGraph graph wiring (nodes, edges, MemorySaver)
│   ├── system_prompt.py  # Behavioural rules for the LLM
│   └── history.py        # Conversation formatter utility
├── tools/
│   ├── schemas.py        # Pydantic input schemas for each tool
│   ├── note_tools.py     # Pure business logic (DB calls, no LLM coupling)
│   └── registry.py       # LangChain @tool wrappers (thread-safe DB access)
├── storage/
│   ├── database.py       # SQLite + FTS5 + triggers + user-scoped queries
│   ├── models.py         # Note dataclass
│   └── embeddings.py     # (Bonus) Semantic search via OpenAI embeddings
├── config.py             # Environment variable loading
├── main.py               # CLI entry point (Rich + argparse)
└── mcp_server.py         # (Bonus) FastMCP server exposing tools to MCP clients
```

### Key Design Decisions

**Why SQLite?**
Zero-config, single-file, ACID-compliant, ships with Python. FTS5 gives full-text search with no extra dependencies. Sufficient at this scale — trivially swappable for Postgres later.

**Why LangGraph?**
Deterministic state machine control over Agent behaviour. Unlike bare function-calling loops, LangGraph makes it explicit which node runs when, making the system easy to debug and extend with new nodes.

**Thread-Safe SQLite**
LangGraph runs `ToolNode` in a separate thread. Instead of a shared connection, each `@tool` call opens and closes its own connection via `_get_db_and_user()`. No connection pools needed.

**Auth Strategy (Stubbed)**
`user_id` is injected server-side via `RunnableConfig` — the LLM never sees or controls it. In production, replace the stub with a JWT-validated ID from a FastAPI middleware layer.

---

## 🔌 MCP Server (Bonus)

Exposes all note tools to any [MCP-compatible client](https://modelcontextprotocol.io) (Claude Desktop, Cursor, etc.):
```bash
python -m src.mcp_server
```

Notes created via MCP are scoped to a server-managed `user_id` namespace.

To wire into Claude Desktop, add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "techlabs_notes": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "env": { "PYTHONPATH": "/path/to/project" }
    }
  }
}
```

---

## 📋 Tool Schema Documentation

See [`docs/tool_schemas.md`](docs/tool_schemas.md) for complete parameter and return type documentation for every tool.

---

## 🐳 Docker (Bonus)

Build and run:

```bash
docker compose up --build
```

This starts the CLI container with `./data` mounted so notes persist between runs.
