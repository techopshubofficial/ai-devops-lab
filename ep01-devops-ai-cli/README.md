# EP01 — DevOps AI CLI

An AI assistant for DevOps engineers, built as a simple command-line tool.

This is **not** a ChatGPT wrapper. The tool reads your real files, extracts the
facts that matter, and then asks the AI to explain them with best practices and
risks. The output is about *your* file, not generic advice.

## What it does (EP01)

```bash
ai explain deployment.yaml
```

1. Reads the Kubernetes YAML file
2. Extracts key facts (kind, replicas, image, resources, probes, ports)
3. Sends that context to the AI
4. Prints: what it does, best practices, risks/security issues, suggestions

## Setup

```bash
# 1. Go into the project
cd ep01-devops-ai-cli

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your OpenAI key
cp .env.example .env
# then edit .env and paste your key
```

## Usage

```bash
# Explain the sample file (has intentional issues for the demo)
python ai.py explain examples/deployment.yaml

# Explain any of your own manifests
python ai.py explain path/to/your/deployment.yaml

# See help
python ai.py --help
```

## Cost

Uses `gpt-4o-mini` by default — the cheapest, fastest model. A single
`explain` call costs a fraction of a cent. Change the model in `.env` via
`OPENAI_MODEL` if you want.

## Security

- `.env` is git-ignored. **Never commit your API key.**
- Only `.env.example` (with a placeholder) is committed.

## Roadmap

| Episode | Command | New idea |
|---------|---------|----------|
| EP01 | `ai explain <file>` | CLI setup + real file context |
| EP02 | `ai review <file>` | Best practices + security scoring |
| EP03 | `ai terraform review main.tf` | New file type, same pattern |
| EP04 | `ai troubleshoot pod <name>` | Live `kubectl` data |
