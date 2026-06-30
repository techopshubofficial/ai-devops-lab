import json
import os
import time
from pathlib import Path

import typer
import yaml
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

load_dotenv()

app = typer.Typer(help="DevOps AI CLI - AI assistant for DevOps engineers.")
console = Console()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def print_banner():
    console.print()
    console.print(Rule(style="cyan"))
    console.print("[bold cyan]  DevOps AI CLI  v0.1[/]")
    console.print("[dim]  AI DevOps Lab — Let's build our own DevOps Copilot[/]")
    console.print(Rule(style="cyan"))
    console.print()


@app.callback()
def main():
    """DevOps AI CLI - AI assistant for DevOps engineers."""
    print_banner()


def get_client() -> OpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        console.print(
            "[bold red]OPENAI_API_KEY not set.[/] Copy .env.example to .env and add your key."
        )
        raise typer.Exit(code=1)
    return OpenAI()


def extract_facts(doc: dict) -> list[tuple[str, str, bool]]:
    """Return (label, value, is_ok) rows pulled from a Kubernetes manifest."""
    rows: list[tuple[str, str, bool]] = []
    rows.append(("Kind", doc.get("kind", "Unknown"), True))
    rows.append(("Name", doc.get("metadata", {}).get("name", "unnamed"), True))

    spec = doc.get("spec", {})
    if "replicas" in spec:
        replicas = spec["replicas"]
        rows.append(("Replicas", str(replicas), replicas > 1))

    pod_spec = spec.get("template", {}).get("spec", spec)
    for c in pod_spec.get("containers", []):
        image = c.get("image", "NOT SET")
        rows.append((f"Container: {c.get('name', 'unnamed')}", image, image != "NOT SET"))
        uses_latest = image.endswith(":latest") or (":" not in image and image != "NOT SET")
        rows.append(("  Image tag", "latest (risky)" if uses_latest else "pinned", not uses_latest))
        rows.append(("  Resources", "set" if c.get("resources") else "NOT SET", bool(c.get("resources"))))
        rows.append(("  Liveness probe", "set" if c.get("livenessProbe") else "MISSING", bool(c.get("livenessProbe"))))
        rows.append(("  Readiness probe", "set" if c.get("readinessProbe") else "MISSING", bool(c.get("readinessProbe"))))
    return rows


def render_facts(file_name: str, rows: list[tuple[str, str, bool]]):
    console.print(f"\n[bold cyan]Reading {file_name}[/]")
    table = Table(show_header=True, header_style="bold magenta", title="Extracted Facts")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for label, value, ok in rows:
        color = "green" if ok else "red"
        table.add_row(label, f"[{color}]{value}[/]")
    console.print(table)
    console.print("[dim]These facts are sent to the AI as context.[/]\n")


def facts_to_text(rows: list[tuple[str, str, bool]]) -> str:
    return "\n".join(f"{label}: {value}" for label, value, _ in rows)


def build_prompt(file_name: str, raw: str, facts: str) -> str:
    return f"""You are a senior DevOps engineer reviewing a real Kubernetes manifest.

File: {file_name}

Extracted facts:
{facts}

Raw YAML:
{raw}

Respond ONLY with JSON in this exact shape:
{{
  "summary": "one or two sentences, plain English, what this manifest does",
  "production_readiness": <integer 1-10, how production-ready this is>,
  "best_practices": ["things it already does well"],
  "problems": ["concrete problems, reference the actual values"],
  "risks": ["security or reliability risks"],
  "suggestions": ["concrete, actionable improvements"],
  "fixed_yaml": "a corrected version of the full YAML that applies your suggestions",
  "fixed_production_readiness": <integer 1-10, estimated score after applying the fixes>
}}

Be specific. Do not invent fields that are not present."""


def score_color(score: int) -> str:
    if score <= 3:
        return "red"
    if score <= 6:
        return "yellow"
    return "green"


def render_section(icon: str, title: str, items: list[str], style: str):
    if not items:
        return
    body = "\n".join(f"  • {item}" for item in items)
    console.print(f"[bold {style}]{icon} {title}[/]\n{body}\n")


def render_result(data: dict):
    score = int(data.get("production_readiness", 0))
    color = score_color(score)

    console.print(Panel(data.get("summary", ""), title="Summary", border_style="cyan"))
    console.print(
        Panel(
            f"[bold {color}]{score} / 10[/]",
            title="[bold]Production Readiness[/]",
            border_style=color,
            subtitle=f"[dim]{'Low — not production-ready' if score <= 3 else 'Needs work' if score <= 6 else 'Looking good'}[/]",
        )
    )
    render_section("❌", "Problems", data.get("problems", []), "red")
    render_section("⚠️ ", "Risks", data.get("risks", []), "yellow")
    render_section("✅", "Best Practices", data.get("best_practices", []), "green")
    render_section("💡", "Suggestions", data.get("suggestions", []), "blue")


@app.command()
def explain(file: Path = typer.Argument(..., help="Path to a Kubernetes YAML file.")):
    """Explain a Kubernetes manifest with context, best practices, and risks."""
    if not file.exists():
        console.print(f"[bold red]File not found:[/] {file}")
        raise typer.Exit(code=1)

    raw = file.read_text()
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        console.print(f"[bold red]Could not parse YAML:[/] {e}")
        raise typer.Exit(code=1)

    if not isinstance(doc, dict):
        console.print("[bold red]This does not look like a single Kubernetes object.[/]")
        raise typer.Exit(code=1)

    rows = extract_facts(doc)
    render_facts(file.name, rows)

    client = get_client()
    start = time.time()
    with console.status("[bold green]🤖 AI is reviewing your manifest...", spinner="dots"):
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": build_prompt(file.name, raw, facts_to_text(rows))}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
    elapsed = time.time() - start

    try:
        data = json.loads(response.choices[0].message.content or "{}")
    except json.JSONDecodeError:
        console.print("[bold red]AI did not return valid JSON. Raw output:[/]")
        console.print(response.choices[0].message.content)
        raise typer.Exit(code=1)

    console.print(Rule(style="cyan"))
    render_result(data)

    console.print(f"[dim]✓ AI review completed in {elapsed:.1f}s[/]\n")

    fixed = data.get("fixed_yaml")
    if fixed and typer.confirm("Generate fixed YAML?"):
        out_path = file.with_name(f"{file.stem}-fixed{file.suffix}")
        out_path.write_text(fixed if fixed.endswith("\n") else fixed + "\n")
        before = int(data.get("production_readiness", 0))
        after = int(data.get("fixed_production_readiness", before))
        before_color = score_color(before)
        after_color = score_color(after)
        console.print(f"[bold green]✔ {out_path.name} generated[/]")
        console.print(
            f"[bold]✔ Production score[/]  "
            f"[bold {before_color}]{before}/10[/] → [bold {after_color}]{after}/10[/]"
        )


if __name__ == "__main__":
    app()
