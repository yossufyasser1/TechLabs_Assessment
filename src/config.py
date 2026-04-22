"""Configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

# We switched to Ollama for local execution (no internet or rate limits needed)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Which LLM provider to use: 'ollama' (default) or 'openai' (fallback/cloud)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Using llama3.1 to ensure tool-calling capabilities exist locally (or gpt-4o-mini for openai)
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.1")

DB_PATH = os.getenv("DB_PATH", "data/notes.db")
