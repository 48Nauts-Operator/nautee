"""
Claude Folder Reviewer

This script scans a folder for source files, batches them together into a single prompt,
and uses Anthropic Claude to return structural code insights in Markdown format.

It focuses on:
- Code organization
- Bug patterns
- Architecture weaknesses
- Suggestions for modularization and clarity
"""

import os
import sys
import anthropic
from dotenv import load_dotenv
from datetime import datetime
import time

def render_progress(current: int, total: int, width: int = 30) -> str:
    """
    Renders a visual progress bar with a percentage.

    Args:
        current (int): Current progress count.
        total (int): Total items to process.
        width (int): Width of the progress bar in characters.

    Returns:
        str: A formatted progress bar string.
    """
    percent = current / total
    filled = int(width * percent)
    bar = "█" * filled + "-" * (width - filled)
    return f"[{bar}] {int(percent * 100)}%"

def estimate_valid_files(folder: str, valid_exts: tuple) -> list:
    """
    Recursively finds all valid source files in a given folder.

    Args:
        folder (str): Root directory to search.
        valid_exts (tuple): Acceptable file extensions.

    Returns:
        list: List of full file paths.
    """
    files = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename.endswith(valid_exts):
                files.append(os.path.join(root, filename))
    return files

def main():
    # === Setup ===
    load_dotenv()
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    folder = sys.argv[1] if len(sys.argv) > 1 else "../137docs"
    os.makedirs("output", exist_ok=True)

    valid_exts = (".py", ".js", ".ts", ".tsx", ".jsx")

    files = estimate_valid_files(folder, valid_exts)
    total_files = len(files)

    if total_files == 0:
        print(f"❌ No valid files found in {folder}")
        sys.exit(1)

    print(f"🔍 Found {total_files} source files in: {folder}\n")

    combined = ""
    reviewed_files = []
    start_time = time.time()

    for idx, file_path in enumerate(files, start=1):
        try:
            with open(file_path, "r") as f:
                code = f.read()
                rel_path = os.path.relpath(file_path, folder)
                combined += f"\n\n### `{rel_path}`\n```python\n{code}\n```"
                reviewed_files.append(rel_path)

            elapsed = time.time() - start_time
            avg_time = elapsed / idx
            remaining = avg_time * (total_files - idx)
            eta = time.strftime("%M:%S", time.gmtime(remaining))
            print(f"{render_progress(idx, total_files)} ⏱ ETA: {eta} | ✅ {rel_path}")

        except Exception as e:
            print(f"[ERR] ❌ Error reading {file_path}: {e}")

    prompt = f"""You are a senior reviewer. Review the following **entire codebase folder** and return insights in **Markdown format**.

Focus on:
- Code organization
- Bug patterns
- Architecture weaknesses
- Suggestions for modularization and clarity

Files:
{combined}
"""

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

if __name__ == "__main__":
    main()