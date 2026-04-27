# Conversational Note-Taking Agent

An intelligent command-line chat agent that lets users manage personal notes entirely through natural language
## Features

| Feature | Details |
|---|---|
| **Natural Language CRUD** | Create, read, update, delete notes via conversation |
| **Full-Text Search** | SQLite FTS5 for fast keyword & tag-based retrieval |
| **Multi-Turn Awareness** | LangGraph MemorySaver keeps full conversation context |
| **Multi-User Isolation** | Notes scoped per `user_id` at the database level |
| **Destructive Action Guards** | Agent confirms before any delete |
| **Local-First (Privacy)** | Default is 100% offline via Ollama. Also supports OpenAI via API Key |
| **Evaluation Harness** | 15 automated conversational scenarios, pass/fail report |
| **Semantic Search**  | Cosine similarity |

---

## Setup

### Prerequisites
- Python 3.10+
- **Option A:** [Ollama](https://ollama.com) installed and running locally
- **Option B:** An OpenAI API Key 

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
```
By default, the `.env` file assumes you are using `LLM_PROVIDER=ollama`. 

**If using OpenAI instead of Ollama:**  
Edit your `.env` file and strictly set:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
MODEL_NAME=gpt-4o-mini
```

### 3. Install local models (Option A only)
If using Ollama, ensure you pull the model:
```bash
ollama pull llama3.1
```

### 4. Run the agent
```bash
python -m src.main
```
Multi-user support (notes are isolated per user):
```bash
python -m src.main --user alice
```

---

## Evaluation Harness

Run the full 15-scenario automated evaluation to test intent disambiguation, error handling, and multi-turn context:
```bash
python -m evals.report
```

---

## Architecture

```
src/
├── agent/
│   ├── agent.py          # LangGraph graph wiring (nodes, edges, MemorySaver)
│   └── system_prompt.py  # Behavioural rules for the LLM
├── tools/
│   ├── schemas.py        # Pydantic input schemas for each tool
│   ├── note_tools.py     # Pure business logic (DB calls, no LLM coupling)
├── storage/
│   ├── database.py       # SQLite + FTS5 + triggers + user-scoped queries
│   ├── models.py         # Note dataclass
│   └── embeddings.py     # Semantic search via local Ollama embeddings
├── config.py             # Environment variable loading
└── main.py               # CLI entry point
```

### Key Design Decisions

**Why SQLite?**
Zero-config, single-file, ACID-compliant, ships with Python. FTS5 gives full-text search with no extra dependencies. Sufficient at this scale — trivially swappable for Postgres later.

**Why LangGraph?**
Deterministic state machine control over Agent behaviour. Unlike bare function-calling loops, LangGraph makes it explicit which node runs when, making the system easy to debug and extend with new nodes.

**Auth Strategy (Stubbed)**
`user_id` is injected server-side via `RunnableConfig` — the LLM never sees or controls it. In production, replace the stub with a JWT-validated ID from a middleware layer.

---

## MCP Server (Bonus)

Exposes all note tools to any [MCP-compatible client](https://modelcontextprotocol.io) (Claude Desktop, Cursor, etc.):
```bash
npx @modelcontextprotocol/inspector python src/mcp_server.py
```

Notes created via MCP are scoped to a server-managed `mcp_client_user` namespace.

---

## Tool Schema Documentation

See `docs/tool_schemas.md` for complete parameter and return type documentation for every tool.

---

## Docker (Bonus)

Build and run:

```bash
docker-compose up --build
```
This starts the CLI container with `./data` mounted locally so notes persist between runs.
