print("\U0001f441 autodoc.py is executing from:", __file__, flush=True)
"""
Autodoc Generator

Scans the project for Python source files, generates Markdown documentation using Claude,
writes to docs/*.md, and updates mkdocs.yml and index.md.
"""

import os
import sys
import anthropic
from dotenv import load_dotenv
from datetime import datetime
import yaml

# === Setup ===

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

target_path = sys.argv[1] if len(sys.argv) > 1 else "."
output_dir = "docs"
os.makedirs(output_dir, exist_ok=True)

mkdocs_yml_path = "mkdocs.yml"
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

# === Helpers ===

def snake_md_path(rel_path: str) -> str:
    return rel_path.replace("/", "_").replace(".", "_") + ".md"

def load_mkdocs_config(path: str):
    if os.path.exists(path):
        with open(path, "r") as f:
            return yaml.safe_load(f)
    return {
        "site_name": "Nautee Docs",
        "theme": {"name": "material"},
        "nav": []
    }

def write_index_md(nav_items):
    index_md_path = os.path.join(output_dir, "index.md")
    with open(index_md_path, "w") as f:
        f.write("# \U0001f4da Auto-Generated Documentation Index\n\n")
        f.write("Welcome to the **Nautee Documentation Portal**. This site contains documentation generated automatically by Claude from Anthropic.\n\n")
        f.write("## \U0001f5c2️ AutoDocs (Generated)\n\n")
        for item in nav_items:
            for title, link in item.items():
                f.write(f"- [{title}]({link})\n")
        f.write(f"\n---\n\n_Last updated: {timestamp}_\n")

def append_missing_docs_to_index(nav_items):
    index_md_path = os.path.join(output_dir, "index.md")
    existing_links = set(link for item in nav_items for link in item.values())

    with open(index_md_path, "a") as f:
        f.write("\n## 🗃️ Other Markdown Files\n\n")
        for root, _, files in os.walk(output_dir):
            for file in files:
                if file.endswith(".md") and file != "index.md":
                    rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                    if rel_path not in existing_links:
                        f.write(f"- [{rel_path}]({rel_path})\n")

def write_mkdocs_config(path: str, static_nav, autodoc_items):
    full_nav = static_nav + [{"AutoDocs": autodoc_items}]
    with open(path, "w") as f:
        yaml.dump({
            "site_name": "Nautee Docs",
            "theme": {
                "name": "material",
                "palette": [
                    {
                        "scheme": "slate",
                        "primary": "blue",
                        "accent": "green",
                        "toggle": {
                            "icon": "material/weather-sunny",
                            "name": "Switch to light mode"
                        }
                    },
                    {
                        "scheme": "default",
                        "primary": "blue",
                        "accent": "green",
                        "toggle": {
                            "icon": "material/weather-night",
                            "name": "Switch to dark mode"
                        }
                    }
                ],
                "font": {
                    "text": "Roboto",
                    "code": "Roboto Mono"
                },
                "features": [
                    "navigation.instant",
                    "navigation.tabs",
                    "navigation.top",
                    "content.code.copy",
                    "content.action.edit",
                    "content.action.view",
                    "content.code.annotate",
                    "search.suggest",
                    "search.highlight"
                ]
            },
            "markdown_extensions": [
                "admonition",
                "codehilite",
                "footnotes",
                "meta",
                {"toc": {"permalink": True}},
                {"pymdownx.highlight": {"anchor_linenums": True, "linenums": True}},
                "pymdownx.superfences",
                "pymdownx.inlinehilite",
                "pymdownx.details",
                "pymdownx.snippets",
                "pymdownx.magiclink",
                "pymdownx.mark",
                {"pymdownx.tasklist": {"custom_checkbox": True}},
                "pymdownx.keys",
                {"pymdownx.emoji": {
                    "emoji_generator": "!!python/name:materialx.emoji.to_svg"
                }}
            ],
            "plugins": [
                "search",
                {
                    "mkdocstrings": {
                        "handlers": {
                            "python": {
                                "options": {
                                    "show_source": True
                                }
                            }
                        }
                    }
                }
            ],
            "nav": full_nav
        }, f, sort_keys=False)

def collect_python_files(base: str):
    results = []
    for root, _, files in os.walk(base):
        for file in files:
            if file.endswith(".py") and not file.startswith("test_") and file != "__init__.py":
                results.append(os.path.join(root, file))
    return results

# === Scan Python Files ===

py_files = collect_python_files(target_path)
if not py_files:
    print("⚠️ No Python files found.")
    sys.exit(0)

print(f"📂 Found {len(py_files)} Python files.\n")

autodoc_nav = []

# === Generate Docs ===

for file_path in py_files:
    try:
        with open(file_path, "r") as f:
            source_code = f.read()

        rel_path = os.path.relpath(file_path, target_path)
        md_filename = snake_md_path(rel_path)
        md_output_path = os.path.join(output_dir, md_filename)

        prompt = f"""You are a technical writer. Generate documentation in Markdown for the following Python file.

Explain what the file does, its purpose, important functions or classes, and give suggestions or notes as needed.

Use headings, bullet points, and code blocks to make it readable.

```python
{source_code}
```"""

        response = client.messages.create(
            model=model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        markdown = response.content[0].text.strip()

        with open(md_output_path, "w") as out:
            out.write(f"<!-- Auto-generated by Claude on {timestamp} -->\n\n")
            out.write(markdown)

        print(f"✅ Documented: {rel_path} → {md_filename}")
        autodoc_nav.append({rel_path.split('/')[-1].replace('.py', ''): md_filename})
        print("🧭 Appending to autodoc_nav:", {rel_path.split('/')[-1].replace('.py', ''): md_filename})

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

# === Update mkdocs.yml ===

print("\n🧠 Loading existing mkdocs.yml...")
existing = load_mkdocs_config(mkdocs_yml_path)
if not existing:
    print("⚠️ No existing config found. A new one will be created.")
else:
    print("✅ Found existing mkdocs.yml")
    print("📄 Current nav section (before):")
    for item in existing.get("nav", []):
        print("   ", item)

# Remove existing AutoDocs
static_nav = [item for item in existing.get("nav", []) if "AutoDocs" not in item]

# Debug new entries
print("\n🧩 New AutoDocs entries to add:")
for item in autodoc_nav:
    print("   ", item)

# Combine new nav
full_nav = static_nav + [{"AutoDocs": autodoc_nav}]

# Write mkdocs.yml
print("\n💾 Writing updated mkdocs.yml...")
write_mkdocs_config(mkdocs_yml_path, static_nav, autodoc_nav)
print("✅ mkdocs.yml updated with latest AutoDocs.")

# === Write index.md ===

print("\n📝 Writing index.md with AutoDocs entries...")
write_index_md(autodoc_nav)
append_missing_docs_to_index(autodoc_nav)
print("✅ index.md updated with all .md files.")