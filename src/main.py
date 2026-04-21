"""
CLI entry point for the conversational note-taking agent.

Run with:
    python -m src.main
    python -m src.main --user alice   # multi-user support
"""

import argparse
import uuid

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from src.agent import agent_executor
from src.config import DB_PATH

console = Console()


def print_welcome():
    console.print(Panel.fit(
        "[bold green]🗒️  Note-Taking Agent[/bold green]\n"
        "[dim]Powered by Ollama (Llama 3.1) + LangGraph[/dim]\n\n"
        "Type your message to manage your notes.\n"
        "[dim]Commands: /quit · /clear · /history[/dim]",
        border_style="green"
    ))


def run(user_id: str = "default"):
    """Start the interactive chat loop."""
    print_welcome()

    # Each conversation gets a unique thread_id so MemorySaver can track it
    thread_id = str(uuid.uuid4())
    config = {
        "configurable": {
            "thread_id": thread_id,
            "db_path": DB_PATH,   # tools open their own per-thread connection
            "user_id": user_id,
        }
    }

    history = []  # local copy for /history command

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue

        # ── Special commands ──────────────────────────────────
        if user_input.lower() == "/quit":
            console.print("[dim]Goodbye![/dim]")
            break

        if user_input.lower() == "/clear":
            console.clear()
            print_welcome()
            # Start a fresh thread so memory resets
            thread_id = str(uuid.uuid4())
            config["configurable"]["thread_id"] = thread_id
            history.clear()
            continue

        if user_input.lower() == "/history":
            if not history:
                console.print("[dim]No conversation history yet.[/dim]")
            else:
                console.print("\n".join(history))
            continue

        # ── Run the agent ─────────────────────────────────────
        history.append(f"You : {user_input}")

        with console.status("[dim]Thinking...[/dim]", spinner="dots"):
            result = agent_executor.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
            )

        # The last message in state is the agent's reply
        agent_reply = result["messages"][-1].content

        history.append(f"Agent: {agent_reply}")

        # Render as Markdown so lists, bold, etc. look nice in the terminal
        console.print("\n[bold green]Agent[/bold green]")
        console.print(Markdown(agent_reply))


def main():
    parser = argparse.ArgumentParser(description="Conversational Note-Taking Agent")
    parser.add_argument(
        "--user",
        default="default",
        help="User ID — notes are isolated per user (default: 'default')",
    )
    args = parser.parse_args()
    run(user_id=args.user)


if __name__ == "__main__":
    main()
