# EP01 — AI CLI Assistant for AWS

> Type plain English → AI generates AWS CLI command → Confirm → Execute → AI explains output

**YouTube:** [Watch EP01 on TechOpsHub](https://youtube.com/@techopshub)

---

## Demo

```
You: Create an EC2 t2.micro instance in us-east-1

╭─ Generated Command ────────────────────────────────────────╮
│  aws ec2 run-instances \                                    │
│    --image-id ami-0c02fb55956c7d316 \                       │
│    --instance-type t2.micro \                               │
│    --region us-east-1 --count 1                             │
╰────────────────────────────────────────────────────────────╯

Run this command? (yes/no): yes

╭─ AI Summary ───────────────────────────────────────────────╮
│  ✅ EC2 instance i-0abc1234567 successfully launched.       │
│     Instance Type : t2.micro                               │
│     Region        : us-east-1                              │
│     State         : pending (will be running in ~30s)      │
╰────────────────────────────────────────────────────────────╯
```

---

## Setup

```bash
# 1. Clone repo
git clone https://github.com/techopshubofficial/ai-devops-lab.git
cd ai-devops-lab/ep01-ai-aws-cli

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your OpenAI key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-...

# 4. Make sure AWS CLI is configured
aws configure

# 5. Run!
python main.py
```

---

## What it can do

| What you type | What it runs |
|---|---|
| `list all S3 buckets` | `aws s3 ls` |
| `create EC2 t2.micro in us-east-1` | `aws ec2 run-instances ...` |
| `list running EC2 instances` | `aws ec2 describe-instances --filters ...` |
| `create S3 bucket named my-bucket` | `aws s3 mb s3://my-bucket` |
| `show IAM users` | `aws iam list-users` |

---

## Files

```
ep01-ai-aws-cli/
├── main.py          # CLI entry point (rich UI, confirm loop)
├── agent.py         # OpenAI calls (generate command + explain output)
├── executor.py      # Safe subprocess runner
├── requirements.txt
└── .env.example
```

---

## Safety Note

The tool only runs commands starting with `aws `. It always asks for confirmation before executing. Never run in production without reviewing the command.
