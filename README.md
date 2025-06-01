# 🤖 Claude GitHub Assistant (V1)

A lightweight toolset to generate local code reviews using **Claude by Anthropic**.
[![Docs](https://img.shields.io/badge/📄-View%20Documentation-blue)](https://github.com/48Nauts-Operator/nautee)
---

## ✨ Features

- 🔍 Review individual files or full project folders
- 🧠 Uses Claude to generate clean, structured Markdown feedback
- 🗂️ Saves all reviews into the `output/` directory
- ✅ Supports reviewing Git diffs with zero config

---

## 🛠️ Setup

1. Copy `.env.sample` to `.env` and add your Claude API key:

```bash
cp .env.sample .env

	2.	Install dependencies:

pip install anthropic python-dotenv

No requirements.txt is needed yet — you can add one later if needed.

⸻

🚀 Usage

🔹 Review specific files

python tools/claude_review.py ../yourrepo/file1.py ../yourrepo/file2.py

🔹 Review current Git diff (staged changes)

python tools/claude_review.py

Automatically detects git diff --staged

🔹 Review an entire folder

python tools/claude_folder_review.py ../yourrepo/

Skips test files and __init__.py by default

⸻

📁 Output

All reviews are saved as Markdown files in the output/ folder:
	•	Named and structured for easy reference
	•	Works with Markdown renderers and editors

⸻

🔐 Local & Secure
	•	Runs entirely locally
	•	No data is stored externally
	•	Your Claude API key stays in your .env file

⸻

🛣️ Roadmap (V2+ Preview)
	•	Add Vector DB + Postgres for issue tracking
	•	Dashboards to monitor bad patterns
	•	LiteLLM support for multi-LLM agents
	•	Integration with Cursor, ClickUp, and Jira
	•	Dev behavior analytics + pattern database

⸻

🧑‍💻 Author

Designed for developers who want instant, intelligent feedback — without giving up local control.
