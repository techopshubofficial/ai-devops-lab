"""
Safe command executor — runs AWS CLI commands and captures output.
"""

import subprocess
import shlex


def run_command(command: str) -> tuple[str, str, int]:
    """
    Run a shell command.
    Returns (stdout, stderr, returncode).
    Only aws commands are allowed for safety.
    """
    stripped = command.strip()
    if not stripped.startswith("aws "):
        return "", "Only AWS CLI commands are allowed.", 1

    try:
        result = subprocess.run(
            shlex.split(stripped),
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except FileNotFoundError:
        return "", "AWS CLI not found. Install it: https://aws.amazon.com/cli/", 1
    except subprocess.TimeoutExpired:
        return "", "Command timed out after 60 seconds.", 1
