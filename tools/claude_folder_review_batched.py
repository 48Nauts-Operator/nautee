"""
Claude Folder Review (Batched)

This script recursively reviews source code files from a folder using Claude in batches.
It automatically splits files into ~10k token chunks and stores individual markdown reviews.
"""

import os
import sys
import anthropic
from dotenv import load_dotenv
from datetime import datetime
import time

def is_excluded(filename: str) -> bool:
    """
    Determines whether a file should be excluded based on its name.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if it's a test file, False otherwise.
    """
    lower = filename.lower()
    return "test" in lower or lower.startswith("test_") or "/test" in lower or "\\test" in lower

def estimate_tokens(text: str) -> int:
    """
    Estimates token count from text based on average token size.

    Args:
        text (str): Source content.

    Returns:
        int: Estimated token count.
    """
    return int(len(text) / 4)

def main():
    # === Setup ===
    load_dotenv()
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    folder = sys.argv[1] if len(sys.argv) > 1 else "../137docs"
    output_root = "docs/folder_review"
    os.makedirs(output_root, exist_ok=True)

    valid_exts = (".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json", ".go", ".java", ".yaml", ".yml")

    # === Discover Files ===
    files = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            if filename.endswith(valid_exts) and not is_excluded(full_path):
                files.append(full_path)

    if not files:
        print(f"❌ No valid files found in {folder}")
        sys.exit(1)

    print(f"🔍 Found {len(files)} valid source files in: {folder}\n")

    # === Token Batching ===
    MAX_TOKENS = 10000
    batches = []
    current_batch = []
    current_tokens = 0

    for file_path in files:
        try:
            with open(file_path, "r") as f:
                code = f.read()
            rel_path = os.path.relpath(file_path, folder)
            entry = f"\n\n### `{rel_path}`\n```python\n{code}\n```"
            est = estimate_tokens(entry)

            if current_tokens + est > MAX_TOKENS:
                batches.append(current_batch)
                current_batch = [entry]
                current_tokens = est
            else:
                current_batch.append(entry)
                current_tokens += est
        except Exception as e:
            print(f"[ERR] ❌ Error reading {file_path}: {e}")

    if current_batch:
        batches.append(current_batch)

    # === Run Batches ===
    start_time = time.time()

    for i, batch in enumerate(batches, start=1):
        print(f"📦 Processing batch {i} of {len(batches)}...")

        prompt = f"""You are a senior reviewer. Review the following batch of files from a codebase folder and return insights in **Markdown format**.

Focus on:
- Code organization
- Bug patterns
- Architecture weaknesses
- Suggestions for modularization and clarity

Files:
{''.join(batch)}
"""

        try:
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            review = response.content[0].text.strip()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            out_path = f"{output_root}/folder_review_batch_{i:02d}.md"

            with open(out_path, "w") as f:
                f.write(f"# 📦 Folder Review Batch {i}\n\n")
                f.write(f"_Last updated: {timestamp}_\n\n")
                f.write(review)

            print(f"✅ Batch {i} saved to {out_path}")

        except Exception as e:
            print(f"❌ Claude API error in batch {i}: {e}")

    total_time = time.strftime("%M:%S", time.gmtime(time.time() - start_time))
    print(f"🎉 All batches complete in {total_time}")

if __name__ == "__main__":
    main()