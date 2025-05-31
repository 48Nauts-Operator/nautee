# =========================
# Review a single file or a git diff
# Author: André Wolke
# Date: 2025-05-31
# Version: 1.0.0
# =========================
import os
import anthropic
from dotenv import load_dotenv
from datetime import datetime

# Load API key and model from .env
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# Create output folder if it doesn't exist
os.makedirs("output", exist_ok=True)

# List of code files you want to document
files_to_doc = [
    "../137docs/main.py",       # Adjust this path to your real source
    "../137docs/processor.py"   # Add more as needed
]

for file_path in files_to_doc:
    if not os.path.exists(file_path):
        print(f"⚠️ Skipping missing file: {file_path}")
        continue

    with open(file_path, "r") as f:
        source_code = f.read()

    filename = os.path.basename(file_path).replace(".", "_")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    out_path = f"output/autodoc_{filename}_{timestamp}.txt"

    prompt = f'''You are a technical writer. Please generate professional, structured documentation in Markdown format for the following code file:
    ```python
    {source_code}
    ```'''