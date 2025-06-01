"""
Claude Review Tool

This script reviews either specified source files or a Git diff using Claude.
Outputs a single Markdown file with structured feedback.
"""

import os
import sys
import anthropic
from dotenv import load_dotenv
from datetime import datetime
import subprocess

def load_code(file_paths):
    """
    Combines file contents into a markdown-formatted string.

    Args:
        file_paths (list): List of file paths.

    Returns:
        str: Markdown-formatted string of source files.
    """
    combined_code = ""
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"⚠️ Skipping missing file: {file_path}")
            continue
        with open(file_path, "r") as f:
            content = f.read()
            combined_code += f"\n\n### `{file_path}`\n```python\n{content}\n```"
    return combined_code

def get_git_diff():
    """
    Attempts to retrieve git diff output.

    Returns:
        str: Git diff string or empty if unavailable.
    """
    try:
        print("📦 Trying `git diff origin/main...HEAD`...")
        return subprocess.check_output(["git", "diff", "origin/main...HEAD"]).decode()
    except subprocess.CalledProcessError:
        print("⚠️ `origin/main` not found. Trying HEAD^...")
        try:
            return subprocess.check_output(["git", "diff", "HEAD^"]).decode()
        except subprocess.CalledProcessError:
            return ""

def main():
    # === Setup ===
    load_dotenv()
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    os.makedirs("docs", exist_ok=True)
    output_path = "docs/claude_review.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    file_paths = sys.argv[1:]

    # === MODE 1: Manual File Review ===
    if file_paths:
        combined_code = load_code(file_paths)
        prompt = f'''You are a senior code reviewer. Please analyze the following files and provide **Markdown-formatted** feedback.

Focus on:
- Bugs or logic issues
- Code clarity
- Suggested improvements
- Style consistency

Code:
{combined_code}
'''

    # === MODE 2: Git Diff Review ===
    else:
        diff = get_git_diff()
        if not diff:
            review_text = "# 🧠 Claude Review\n\n⚠️ No diff available — skipping review."
            with open(output_path, "w") as f:
                f.write(review_text)
            print(f"📝 Stub review saved to `{output_path}`")
            sys.exit(0)

        prompt = f'''You are a senior code reviewer. Please review the following GitHub diff and return your structured feedback in **Markdown format**.

```diff
{diff}
```'''

    # === Claude API Call ===
    try:
        response = client.messages.create(
            model=model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        review_text = response.content[0].text.strip()
        with open(output_path, "w") as f:
            f.write(f"# 🧠 Claude Review\n\n")
            f.write(f"_Last updated: {timestamp}_\n\n")
            f.write(review_text)

        print(f"✅ Markdown review saved to `{output_path}`")

    except Exception as e:
        print("❌ Claude API error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()