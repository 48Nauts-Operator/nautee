import os
import sys
import anthropic
from dotenv import load_dotenv
from datetime import datetime

# === Load .env and Claude Setup ===
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# === Get target path ===
target_path = sys.argv[1] if len(sys.argv) > 1 else "."
output_dir = "output/autodoc"
os.makedirs(output_dir, exist_ok=True)

# === Walk all .py files recursively ===
py_files = []
for root, _, files in os.walk(target_path):
    for file in files:
        if file.endswith(".py") and not file.startswith("test_") and file != "__init__.py":
            py_files.append(os.path.join(root, file))

if not py_files:
    print("⚠️ No Python files found to document.")
    sys.exit(0)

print(f"📂 Found {len(py_files)} Python files to document.")

# === Loop through each file and document ===
for file_path in py_files:
    try:
        with open(file_path, "r") as f:
            source_code = f.read()

        rel_path = os.path.relpath(file_path, start=target_path).replace("/", "_").replace(".", "_")
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        out_path = os.path.join(output_dir, f"autodoc_{rel_path}_{timestamp}.md")

        prompt = f'''You are a technical writer. Please generate professional, clear documentation in Markdown format for the following Python code:

```python
{source_code}
```'''

        response = client.messages.create(
            model=model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        markdown = response.content[0].text.strip()

        with open(out_path, "w") as out_file:
            out_file.write(markdown)

        print(f"✅ Documented: {file_path} → {out_path}")

    except Exception as e:
        print(f"❌ Error documenting {file_path}: {e}")