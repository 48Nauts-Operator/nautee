"""
Changelog Generator

Summarizes recent Git commit messages using Claude and writes a formatted changelog to docs/changelog.md.
"""

import os
import anthropic
from dotenv import load_dotenv
from datetime import datetime
import subprocess

def get_git_log(n=20):
    """Fetch recent Git commit messages."""
    try:
        return subprocess.check_output([
            "git", "log", f"--pretty=format:* %s", f"-n", str(n)
        ]).decode()
    except Exception as e:
        print("❌ Error reading git log:", e)
        return "# No commits found"

def format_prompt(git_log: str) -> str:
    """Creates a prompt to summarize commit messages."""
    return f"""You are a changelog assistant. Summarize the following commit messages into clear, readable release notes:
Use markdown formatting with sections like 'Features', 'Fixes', 'Improvements' if applicable.

Commits:
{git_log}
"""

def main():
    load_dotenv()
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    git_log = get_git_log()
    prompt = format_prompt(git_log)

    response = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    notes = response.content[0].text.strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    output_path = "docs/changelog.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 📝 Changelog\n\n")
        f.write(f"_Last updated: {timestamp}_\n\n")
        f.write(notes)

    print(f"✅ Changelog written to {output_path}")

if __name__ == "__main__":
    main()