# 🤖 AI DevOps Lab

> AI-powered tools for DevOps engineers — CLI assistants, log analyzers, YAML generators, Terraform writers and more. Built with Python + OpenAI/Claude.

[![YouTube](https://img.shields.io/badge/YouTube-TechOpsHub-red?logo=youtube)](https://youtube.com/@techopshub)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📺 Video Series

| Episode | Topic | Folder | Status |
|---------|-------|--------|--------|
| EP01 | AI CLI Assistant for AWS (EC2, S3) | [ep01-ai-aws-cli](./ep01-ai-aws-cli/) | ✅ Live |
| EP02 | AI Bash Script Generator | `ep02-ai-bash-generator` | 🔜 Coming |
| EP03 | AI Dockerfile Generator | `ep03-ai-dockerfile-generator` | 🔜 Coming |
| EP04 | AI Terraform Generator | `ep04-ai-terraform-generator` | 🔜 Coming |
| EP05 | AI Kubernetes Error Explainer | `ep05-ai-k8s-explainer` | 🔜 Coming |
| EP06 | AI Log Analyzer (CloudWatch) | `ep06-ai-log-analyzer` | 🔜 Coming |
| EP07 | AI YAML Generator | `ep07-ai-yaml-generator` | 🔜 Coming |
| EP08 | AI IAM Policy Generator | `ep08-ai-iam-generator` | 🔜 Coming |
| EP09 | AI GitHub Actions Generator | `ep09-ai-github-actions` | 🔜 Coming |
| EP10 | AI DevOps Chatbot (All-in-One) | `ep10-ai-devops-chatbot` | 🔜 Coming |

---

## EP01 — AI CLI Assistant for AWS

**"AI ne mere liye EC2 bana di — bina console khole"**

Type plain English → AI generates AWS CLI command → Confirm → Execute → AI explains output.

```
You: Create an EC2 t2.micro instance in us-east-1

AI Command:
  aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t2.micro \
    --region us-east-1

Run this command? (yes/no): yes

✅ Done! EC2 instance i-0abc1234567 launched.
   Public IP : 3.92.14.55
   State     : pending → running
```

### Quick Start

```bash
cd ep01-ai-aws-cli
pip install -r requirements.txt
cp .env.example .env        # add your OpenAI API key
python main.py
```

### Requirements
- Python 3.11+
- AWS CLI configured (`aws configure`)
- OpenAI API key

---

## 🗂 Repo Structure

```
ai-devops-lab/
├── ep01-ai-aws-cli/
│   ├── main.py
│   ├── agent.py
│   ├── executor.py
│   ├── requirements.txt
│   └── .env.example
├── ep02-ai-bash-generator/   (coming soon)
└── ...
```

---

## 🤝 Contributing

Star ⭐ the repo if you find it useful. PRs welcome.

---

## 📄 License

MIT
