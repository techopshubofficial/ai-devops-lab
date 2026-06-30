import os
from pathlib import Path

import typer
import yaml
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = typer.Typer(help="DevOps AI CLI - AI assistant for DevOps engineers.")

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@app.callback()
def main():
    """DevOps AI CLI - AI assistant for DevOps engineers."""


def get_client() -> OpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        typer.secho(
            "OPENAI_API_KEY not set. Copy .env.example to .env and add your key.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)
    return OpenAI()


def summarize_k8s(doc: dict) -> str:
    """Pull the facts that matter out of a Kubernetes manifest."""
    facts: list[str] = []
    kind = doc.get("kind", "Unknown")
    name = doc.get("metadata", {}).get("name", "unnamed")
    facts.append(f"Kind: {kind}")
    facts.append(f"Name: {name}")

    spec = doc.get("spec", {})
    if "replicas" in spec:
        facts.append(f"Replicas: {spec['replicas']}")

    pod_spec = spec.get("template", {}).get("spec", spec)
    containers = pod_spec.get("containers", [])
    for c in containers:
        facts.append(f"\nContainer: {c.get('name', 'unnamed')}")
        facts.append(f"  Image: {c.get('image', 'NOT SET')}")
        resources = c.get("resources")
        facts.append(f"  Resources: {resources if resources else 'NOT SET'}")
        facts.append(f"  Liveness probe: {'yes' if c.get('livenessProbe') else 'NOT SET'}")
        facts.append(f"  Readiness probe: {'yes' if c.get('readinessProbe') else 'NOT SET'}")
        ports = [p.get("containerPort") for p in c.get("ports", [])]
        facts.append(f"  Ports: {ports if ports else 'none'}")

    return "\n".join(facts)


def build_prompt(file_name: str, raw: str, facts: str) -> str:
    return f"""You are a senior DevOps engineer reviewing a real Kubernetes manifest.

File: {file_name}

Extracted facts:
{facts}

Raw YAML:
{raw}

Explain this file to another engineer. Structure your answer as:
1. What this manifest does (plain English, short).
2. Best practices it already follows.
3. Problems, risks, or security issues (be specific, reference the actual values).
4. Concrete suggestions to improve it.

Be practical and concise. Do not invent fields that are not present."""


@app.command()
def explain(file: Path = typer.Argument(..., help="Path to a Kubernetes YAML file.")):
    """Explain a Kubernetes manifest with context, best practices, and risks."""
    if not file.exists():
        typer.secho(f"File not found: {file}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    raw = file.read_text()
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        typer.secho(f"Could not parse YAML: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    facts = summarize_k8s(doc) if isinstance(doc, dict) else "Not a single Kubernetes object."

    typer.secho(f"\nReading {file.name} ...\n", fg=typer.colors.CYAN)

    client = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": build_prompt(file.name, raw, facts)}],
        temperature=0.2,
    )
    typer.echo(response.choices[0].message.content)


if __name__ == "__main__":
    app()
