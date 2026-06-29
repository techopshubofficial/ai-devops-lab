"""
EP01 — AI CLI Assistant for AWS
YouTube: TechOpsHub
GitHub : github.com/techopshubofficial/ai-devops-lab
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.spinner import Spinner
from rich import print as rprint
from rich.live import Live
from agent import generate_command, explain_output
from executor import run_command

console = Console()


def print_banner():
    console.print(
        Panel.fit(
            "[bold cyan]🤖 AI AWS CLI Assistant[/bold cyan]\n"
            "[dim]Type what you want to do in plain English[/dim]\n"
            "[dim]Type 'exit' or Ctrl+C to quit[/dim]",
            border_style="cyan",
        )
    )


def handle_request(user_input: str):
    # Step 1: Generate command
    with console.status("[bold yellow]Thinking...[/bold yellow]", spinner="dots"):
        try:
            command = generate_command(user_input)
        except Exception as e:
            console.print(f"[bold red]AI Error:[/bold red] {e}")
            return

    # Step 2: Show generated command
    console.print("\n[bold green]Generated Command:[/bold green]")
    syntax = Syntax(command, "bash", theme="monokai", word_wrap=True)
    console.print(Panel(syntax, border_style="green"))

    # Step 3: Confirm before running
    if not Confirm.ask("\n[bold]Run this command?[/bold]", default=False):
        console.print("[dim]Skipped.[/dim]\n")
        return

    # Step 4: Execute
    console.print()
    with console.status("[bold yellow]Running...[/bold yellow]", spinner="dots"):
        stdout, stderr, returncode = run_command(command)

    # Step 5: Show raw output
    if stdout:
        console.print("[bold white]Output:[/bold white]")
        console.print(Panel(stdout, border_style="white"))

    if stderr:
        color = "red" if returncode != 0 else "yellow"
        console.print(f"[bold {color}]{'Error' if returncode != 0 else 'Warning'}:[/bold {color}]")
        console.print(Panel(stderr, border_style=color))

    # Step 6: AI explains what happened
    console.print()
    with console.status("[bold yellow]Explaining output...[/bold yellow]", spinner="dots"):
        try:
            explanation = explain_output(command, stdout, stderr)
        except Exception:
            explanation = None

    if explanation:
        icon = "✅" if returncode == 0 else "❌"
        console.print(
            Panel(
                f"{icon} {explanation}",
                title="[bold]AI Summary[/bold]",
                border_style="cyan",
            )
        )

    console.print()


def main():
    print_banner()
    console.print()

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Bye![/dim]")
            sys.exit(0)

        user_input = user_input.strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "q"}:
            console.print("[dim]Bye![/dim]")
            sys.exit(0)

        handle_request(user_input)


if __name__ == "__main__":
    main()
