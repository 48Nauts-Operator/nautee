import os
import sys
import anthropic
from dotenv import load_dotenv
from datetime import datetime
import subprocess

# Load Claude config
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# Output folder
os.makedirs("output", exist_ok=True)

# Determine mode: manual file review or Git diff
file_paths = sys.argv[1:]

if file_paths:
    # Manual file review
    combined_code = ""
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"⚠️ Skipping missing file: {file_path}")
            continue
        with open(file_path, "r") as f:
            content = f.read()
            combined_code += f"\n\n### `{file_path}`\n```python\n{content}\n```"

    prompt = f'''You are a senior code reviewer. Please analyze the following files and provide **Markdown-formatted** feedback.

Focus on:
- Bugs or logic issues
- Code clarity
- Suggested improvements
- Style consistency

Code:
{combined_code}
'''
    name_part = "_".join(
        os.path.basename(p).replace(".", "_") for p in file_paths
    )

else:
    # Try Git diff between origin/main and HEAD
    try:
        print("📦 Trying `git diff origin/main...HEAD`...")
        diff = subprocess.check_output(["git", "diff", "origin/main...HEAD"]).decode()
        name_part = "git_diff_origin_main"

    except subprocess.CalledProcessError as e:
        print("⚠️ `origin/main` not found. Falling back to `git diff HEAD^`.")
        try:
            diff = subprocess.check_output(["git", "diff", "HEAD^"]).decode()
            name_part = "git_diff_head_prev"
        except subprocess.CalledProcessError as e2:
            print("❌ Git diff failed. No diff available.")
            sys.exit(1)

    prompt = f'''You are a senior code reviewer. Please review the following GitHub diff and return your structured feedback in **Markdown format**.

```diff
{diff}
```'''

# Claude API call
try:
    response = client.messages.create(
        model=model,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    review_text = response.content[0].text.strip()
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    out_path = f"output/claude_review_{name_part}_{timestamp}.md"

    with open(out_path, "w") as f:
        f.write(review_text)

    print(f"✅ Markdown review saved to {out_path}")

except Exception as e:
    print("❌ Claude API error:", e)
    sys.exit(1)