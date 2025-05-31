# `tools/claude_folder_review.py`

_Last updated: 2025-05-31 15:54_

```python
# =========================
# Review a single file or a git diff
# Author: André Wolke
# Date: 2025-05-31
# Version: 1.0.0
# Description: This script reviews a folder of code using Claude.
# It can be used to review a folder of code.
# =========================

import os
import sys
import anthropic
from dotenv import load_dotenv
from datetime import datetime
import time

# Load environment
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# Target folder
folder = sys.argv[1] if len(sys.argv) > 1 else "../137docs"
os.makedirs("output", exist_ok=True)

# Acceptable file types
valid_exts = (".py", ".js", ".ts", ".tsx", ".jsx")
## valid_exts = (".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json", ".go", ".java", ".yaml", ".yml")

# Discover all matching files
files = []
for root, _, filenames in os.walk(folder):
    for filename in filenames:
        if filename.endswith(valid_exts):
            files.append(os.path.join(root, filename))

total_files = len(files)
if total_files == 0:
    print(f"❌ No valid files found in {folder}")
    sys.exit(1)

print(f"🔍 Found {total_files} source files in: {folder}\n")

combined = ""
reviewed_files = []
start_time = time.time()

# Helper: progress bar
def render_progress(current, total, width=30):
    percent = current / total
    filled = int(width * percent)
    bar = "█" * filled + "-" * (width - filled)
    return f"[{bar}] {int(percent * 100)}%"

for idx, file_path in enumerate(files, start=1):
    try:
        with open(file_path, "r") as f:
            code = f.read()
            rel_path = os.path.relpath(file_path, folder)
            combined += f"\n\n### `{rel_path}`\n```python\n{code}\n```"
            reviewed_files.append(rel_path)

        # ETA
        elapsed = time.time() - start_time
        avg_time = elapsed / idx
        remaining = avg_time * (total_files - idx)
        eta = time.strftime("%M:%S", time.gmtime(remaining))

        # Display progress
        progress_bar = render_progress(idx, total_files)
        print(f"{progress_bar} ⏱ ETA: {eta} | ✅ {rel_path}")

    except Exception as e:
        print(f"[ERR] ❌ Error reading {file_path}: {e}")

# Final Claude prompt
prompt = f"""You are a senior reviewer. Review the following **entire codebase folder** and return insights in **Markdown format**.

Focus on:
- Code organization
- Bug patterns
- Architecture weaknesses
- Suggestions for modularization and clarity

Files:
{combined}
"""

# Claude call
try:
    response = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    review = response.content[0].text.strip()
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    out_path = f"output/folder_review_{timestamp}.md"

    with open(out_path, "w") as f:
        f.write(review)

    total_time = time.strftime("%M:%S", time.gmtime(time.time() - start_time))
    print(f"\n✅ Folder review saved to `{out_path}` in {total_time}")
    print("\n📁 Files Reviewed:")
    for path in reviewed_files:
        print(f"  - {path}")

except Exception as e:
    print("❌ Claude API error:", e)

```