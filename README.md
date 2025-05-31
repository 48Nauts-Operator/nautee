# Claude GitHub Assistant

This toolset includes scripts to:

- 🔍 Review individual files or git diffs using Claude
- 🗂️ Recursively review an entire codebase folder
- ✅ Output structured Markdown reviews to `output/`

## Setup

1. Copy `.env.sample` to `.env` and add your API key
2. Install dependencies:
```bash
pip install anthropic python-dotenv
```

## Usage

### Review one or more files:
```bash
python tools/claude_review.py ../yourrepo/file1.py ../yourrepo/file2.py
```

### Review git diff:
```bash
python tools/claude_review.py
```

### Review entire folder recursively:
```bash
python tools/claude_folder_review.py ../yourrepo/
```

Markdown results will be saved in the `output/` folder.
