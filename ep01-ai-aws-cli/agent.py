"""
AI Agent: converts plain English → AWS CLI command
Uses OpenAI GPT-4o (or Claude if you swap the client)
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are an AWS CLI expert assistant.

When the user describes what they want to do on AWS, you MUST:
1. Output ONLY the exact AWS CLI command(s) needed — nothing else.
2. Use real, correct flags and realistic placeholder values (e.g., ami-0c02fb55956c7d316 for Amazon Linux 2 in us-east-1).
3. If multiple commands are needed, put each on its own line.
4. Do NOT add explanations, markdown fences, or commentary in this step.

Examples:
User: "list all S3 buckets"
Output: aws s3 ls

User: "create EC2 t2.micro in us-east-1"
Output: aws ec2 run-instances --image-id ami-0c02fb55956c7d316 --instance-type t2.micro --region us-east-1 --count 1

User: "delete S3 bucket named my-test-bucket"
Output: aws s3 rb s3://my-test-bucket --force
"""

EXPLAIN_PROMPT = """You are a helpful DevOps assistant.

The user just ran an AWS CLI command. Explain the output in 2-4 lines:
- What happened (success or error)
- Key values to note (instance ID, IP, bucket name, ARN, etc.)
- Any next step they should know

Be concise. Use plain English. No markdown.
"""


def generate_command(user_input: str) -> str:
    """Convert natural language to AWS CLI command."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
        temperature=0,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


def explain_output(command: str, output: str, error: str) -> str:
    """Explain what happened after running the command."""
    content = f"Command: {command}\n\nOutput:\n{output or '(no output)'}\n\nError:\n{error or '(none)'}"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": EXPLAIN_PROMPT},
            {"role": "user", "content": content},
        ],
        temperature=0.3,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()
