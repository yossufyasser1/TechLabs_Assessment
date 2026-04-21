# Junior Focus Guide (What To Learn First)

If the codebase feels overwhelming, focus only on these files first.  
This is enough to explain the full assessment implementation.

## 1) Main user flow (must know)

- `src/main.py`  
  CLI loop: reads user input, sends it to the agent, prints response.

- `src/agent/agent.py`  
  Defines the graph:
  - chatbot node (LLM thinks)
  - tools node (runs DB tools)
  - loop until no tool call

- `src/agent/system_prompt.py`  
  Behavioral rules: disambiguation, confirmation, no hallucination.

## 2) Tool layer (must know)

- `src/tools/schemas.py`  
  Input contracts for each tool (typed arguments).

- `src/tools/registry.py`  
  Tool wrappers exposed to the LLM.  
  Also injects `user_id` and DB path from runtime config.

- `src/tools/note_tools.py`  
  Plain business logic.  
  This file is easy to explain: each function maps to one CRUD action.

## 3) Storage layer (must know)

- `src/storage/database.py`  
  SQLite operations and FTS search.
  Core methods:
  - `create`
  - `list_notes`
  - `get` (user-scoped)
  - `update` (user-scoped)
  - `delete` (user-scoped)

## 4) Evaluation (must know)

- `tests/eval/scenarios.py`  
  15 conversational test scenarios.

- `tests/eval/harness.py`  
  Runs one scenario and checks pass/fail heuristics.

- `tests/eval/report.py`  
  Runs all scenarios and prints a report table.

## Optional/Bonus (safe to say in interview)

You can explain these as bonus and not core:
- `src/mcp_server.py` (MCP integration)
- semantic embedding-related code
- Docker files

## 2-minute explanation script

"User types in CLI (`main.py`). The message goes to a LangGraph agent (`agent.py`) with memory for multi-turn context.  
The model follows strict behavior rules from `system_prompt.py` and calls typed tools from `registry.py`.  
Tool functions delegate to simple business logic in `note_tools.py`, which uses `database.py` for SQLite CRUD and FTS search.  
All note-by-id operations are user-scoped for isolation.  
Behavior is validated with 15 scenario-based eval tests in `tests/eval`."
