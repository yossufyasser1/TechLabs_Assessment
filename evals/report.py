"""
Generates the Evaluation Report.
Run this file directly to execute the harness: `python -m tests.eval.report`
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from rich.console import Console
from rich.table import Table

from src.storage.database import NoteDatabase
from evals.scenarios import SCENARIOS
from evals.harness import run_scenario

console = Console()

def run_all_evaluations():
    console.print("\n[bold cyan]🚀 Starting Agent Evaluation Harness...[/bold cyan]")
    
    # We use a temporary database for the evaluation
    db_path = "data/eval_test.db"
    if Path(db_path).exists():
        Path(db_path).unlink()
        
    db = NoteDatabase(db_path)
    
    results = []
    passed = 0
    failed = 0
    
    with console.status("[dim]Running 15 conversational scenarios...[/dim]"):
        for scenario in SCENARIOS:
            res = run_scenario(scenario, db)
            results.append(res)
            if res.pass_status:
                passed += 1
            else:
                failed += 1

    db.close()
    
    # Render Report Table
    table = Table(title="Agent Accuracy Report")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Scenario", style="magenta")
    table.add_column("Status", justify="center")
    table.add_column("Details", style="dim")
    
    for r in results:
        status_icon = "[green]PASS[/green]" if r.pass_status else "[red]FAIL[/red]"
        table.add_row(str(r.scenario_id), r.name, status_icon, r.reason)
        
    console.print(table)
    
    # Summary Metrics
    total = len(SCENARIOS)
    pass_rate = (passed / total) * 100
    
    console.print(f"\n[bold]Total Scenarios:[/bold] {total}")
    console.print(f"[bold green]Passed:[/bold green] {passed}")
    console.print(f"[bold red]Failed:[/bold red] {failed}")
    
    if pass_rate == 100:
        console.print(f"[bold green]Pass Rate: {pass_rate:.1f}% 🎉[/bold green]\n")
    elif pass_rate > 80:
        console.print(f"[bold yellow]Pass Rate: {pass_rate:.1f}% ⚠️[/bold yellow]\n")
    else:
        console.print(f"[bold red]Pass Rate: {pass_rate:.1f}% ❌[/bold red]\n")


if __name__ == "__main__":
    run_all_evaluations()
