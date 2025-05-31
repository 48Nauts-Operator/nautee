import os
from datetime import datetime

SOURCE_DIR = "tools"
OUTPUT_DIR = "docs"
INDEX_FILE = os.path.join(OUTPUT_DIR, "index.md")
MKDOCS_FILE = "mkdocs.yml"

def normalize_filename(py_path: str) -> str:
    """Convert a python file path like tools/changelog.py → tools_changelog.md"""
    return py_path.replace("/", "_").replace(".py", "") + ".md"

def extract_title(py_path: str) -> str:
    return os.path.basename(py_path).replace(".py", "").replace("_", " ").title()

def generate_markdown(py_path: str, output_path: str):
    """Write a simple Markdown header from the Python file content."""
    with open(py_path, "r", encoding="utf-8") as f:
        content = f.read()

    mod_time = datetime.fromtimestamp(os.path.getmtime(py_path))
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"# `{py_path}`\n\n")
        out.write(f"_Last updated: {mod_time.strftime('%Y-%m-%d %H:%M')}_\n\n")
        out.write("```python\n")
        out.write(content)
        out.write("\n```")

def cleanup_old_docs():
    for filename in os.listdir(OUTPUT_DIR):
        if filename.startswith("autodoc_tools_") and filename.endswith(".md"):
            os.remove(os.path.join(OUTPUT_DIR, filename))
        if filename.startswith("tools_") and filename.endswith(".md"):
            os.remove(os.path.join(OUTPUT_DIR, filename))

def main():
    cleanup_old_docs()

    docs = []
    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, ".")
                output_name = normalize_filename(relative_path)
                output_path = os.path.join(OUTPUT_DIR, output_name)
                generate_markdown(relative_path, output_path)
                docs.append((relative_path, output_name, extract_title(relative_path)))

    # Write index.md
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("# 📚 Auto-Generated Documentation Index\n\n")
        f.write("Welcome to the Nautee documentation portal. These are the current tools:\n\n")
        for _, output_name, title in sorted(docs):
            f.write(f"- [{title}]({output_name})\n")

    # Update mkdocs.yml
    nav_block = "nav:\n  - Home: index.md\n  - AutoDocs:\n"
    for _, output_name, title in sorted(docs):
        nav_block += f"      - {title}: {output_name}\n"

    with open(MKDOCS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(MKDOCS_FILE, "w", encoding="utf-8") as f:
        inside_nav = False
        for line in lines:
            if line.strip().startswith("nav:"):
                inside_nav = True
                f.write(nav_block)
                continue
            if inside_nav:
                if line.strip() == "" or line.startswith("#"):
                    f.write(line)
                continue
            f.write(line)

if __name__ == "__main__":
    main()