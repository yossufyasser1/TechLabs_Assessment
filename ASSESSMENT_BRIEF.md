# TechLabs London | AI Engineer — Technical Assessment

**Conversational Note-Taking Agent**
Estimated time: 72 hours

## 1. Overview
This assessment asks you to build a conversational note-taking agent — a chat-based system that lets a user manage personal notes entirely through natural language. The goal is not a polished product; we want to see how you think about conversational AI, tool design, state management, and edge cases.
There is no single “right” answer. We care more about your design decisions, reasoning, and how you handle ambiguity than about pixel-perfect code.

## 2. Task Description
Build a command-line or simple web-based chat agent where a user can perform the following actions through natural language conversation:

### 2.1 Core Capabilities
1. **Add notes** — create a new note with a title, body text, and optional tags or categories. Example: “Save a note about the team standup — we agreed to move it to Tuesdays, tag it as meetings.”
2. **List & search notes** — retrieve notes by keyword, tag, date, or a natural language query. Example: “What did I write about the API last week?”
3. **Modify notes** — update the content, title, or tags of an existing note. Example: “Update my standup note to say the meeting is now on Wednesdays.”
4. **Delete notes** — remove a note by reference. Example: “Delete the note about the old office address.”
5. **Answer questions about notes** — summarise, compare, or reason over existing notes. Example: “Summarise everything I’ve tagged as urgent” or “Do I have any notes that contradict each other?”

### 2.2 Required Behaviours
- **Intent disambiguation:** If a user’s request is ambiguous and multiple notes match, the agent must ask for clarification rather than guessing.
- **Confirmation on destructive actions:** Deleting or significantly modifying a note should require explicit user confirmation.
- **Multi-turn awareness:** The agent should handle follow-up messages that reference previous turns (e.g. “Actually, add a deadline to that last note”).
- **Graceful error handling:** When a search returns no results or an action fails, the agent should communicate this clearly and suggest alternatives.
- **Evaluation harness:** Build a small automated test suite with 10–15 conversational scenarios (happy path + edge cases) and report pass/fail rates. Show how you’d measure whether the agent is correctly interpreting intent.

## 3. Technical Requirements
- Language: Python (preferred). TypeScript also accepted.
- LLM integration: Use any LLM provider (OpenAI, Anthropic, open-source, etc.). We will not evaluate your choice of model — we’re evaluating how you use it.
- **Tool / function schema:** Define your own tool schemas for the CRUD operations. This is a key evaluation point — we want to see how you decompose actions into clean, welltyped tool interfaces.
- Persistence: Notes must persist across conversation turns. Use SQLite, a JSON file, or any lightweight storage you prefer. Justify your choice briefly.
- No UI requirement: A terminal-based interface is perfectly fine. If you build a web UI, keep it minimal — we are not evaluating frontend skills in this task.

## 4. Bonus Challenges (Optional)
These are not required but will strengthen your submission. Attempt only after the core task is solid.
- Semantic search
- MCP server implementation
- Multi-user isolation
- Containerisation

## 5. What to Submit
1. Source code in a Git repository (GitHub or GitLab). Clean commit history is appreciated but not required.
2. README with setup instructions (dependencies, environment variables, how to run).
3. Tool schema documentation — a clear description of each tool/function the agent can call, its parameters, and return types.
