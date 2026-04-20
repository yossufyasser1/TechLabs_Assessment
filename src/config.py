"""Configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

# We switched to Google Gemini for free, fast tool-calling inference
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Gemini 1.5 Flash is highly capable of tool calling and very fast/free
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")

DB_PATH = os.getenv("DB_PATH", "data/notes.db")
