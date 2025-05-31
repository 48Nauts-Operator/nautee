# `tools/changelog.py`

_Last updated: 2025-05-31 12:34_

```python
import os
import anthropic
from dotenv import load_dotenv
from datetime import datetime
import subprocess

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# Get commit messages (last 10 as example)
try:
    git_log = subprocess.check_output([
        "git", "log", "--pretty=format:* %s", "-n", "10"
    ]).decode()
except Exception as e:
    print("❌ Error reading git log:", e)
    git_log = "# No commits found"

prompt = f"""You are a changelog assistant. Summarize the following commit messages into clear, readable release notes:
Use markdown formatting with sections like 'Features', 'Fixes', 'Improvements' if applicable.

Commits:
{git_log}
"""

response = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=[{"role": "user", "content": prompt}]
)

notes = response.content[0].text.strip()

# Save output
os.makedirs("output", exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
out_path = f"output/changelog_{timestamp}.txt"

with open(out_path, "w") as f:
    f.write(notes)

print(f"✅ Changelog saved to {out_path}")
```