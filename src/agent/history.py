"""
Conversation history helpers.

LangGraph's MessagesState already stores the full message list automatically.
This module provides a thin helper to format the history into a readable string
— useful for debugging and for the evaluation harness.
"""

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


def format_history(messages: list) -> str:
    """
    Return a readable text representation of a conversation's message list.
    Skips raw ToolMessages (database payloads) to keep output human-friendly.
    """
    lines = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            lines.append(f"User : {msg.content}")
        elif isinstance(msg, AIMessage) and msg.content:
            lines.append(f"Agent: {msg.content}")
        # ToolMessages are internal — we intentionally skip them here
    return "\n".join(lines)
