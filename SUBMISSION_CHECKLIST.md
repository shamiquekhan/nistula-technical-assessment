# Submission Checklist — Nistula Technical Assessment

## Before You Submit

### Part 1: Guest Message Handler (FastAPI)

- [ ] **Environment setup**
  - [ ] Python 3.11+ installed
  - [ ] Virtual environment created (`venv/`)
  - [ ] Dependencies installed (`pip install -r requirements.txt`)
  - [ ] `.env` file created with valid `ANTHROPIC_API_KEY`

- [ ] **Core implementation**
  - [ ] `src/models.py` — Pydantic models for input/output ✅
  - [ ] `src/classifier.py` — Query type classifier ✅
  - [ ] `src/property_context.py` — Mock property data ✅
  - [ ] `src/claude_client.py` — Claude API integration ✅
  - [ ] `src/main.py` — FastAPI application ✅

- [ ] **Testing**
  - [ ] Server starts without errors: `uvicorn src.main:app --reload`
  - [ ] Health endpoint works: `curl http://localhost:8000/health`
  - [ ] Swagger UI loads: visit `http://localhost:8000/docs`
  - [ ] Can send test payloads (see `tests/test_webhook.py` examples)
  - [ ] Responses include: `message_id`, `query_type`, `drafted_reply`, `confidence_score`, `action`

- [ ] **Code quality**
  - [ ] No syntax errors
  - [ ] Imports are correct (no circular dependencies)
  - [ ] Docstrings on all functions
  - [ ] Type hints throughout (Python 3.11+)

### Part 2: PostgreSQL Schema

- [ ] **Schema file**
  - [ ] `schema.sql` is present ✅
  - [ ] All tables created: `unified_messages`, `drafted_replies`, `sent_replies`, `properties`, `bookings`, `agent_actions`
  - [ ] All indexes defined
  - [ ] Foreign key relationships correct
  - [ ] Comments document design decisions

- [ ] **Testing (optional)**
  - [ ] Can execute schema against a local PostgreSQL instance
  - [ ] No syntax errors in SQL

### Part 3: Thinking Questions

- [ ] **Written responses**
  - [ ] `thinking.md` is present ✅
  - [ ] Addresses the 3 AM complaint scenario
  - [ ] Explains system response, confidence score, and action
  - [ ] Describes how a human agent gets involved
  - [ ] Considers alternative approaches
  - [ ] Clear, well-structured writing

### Documentation

- [ ] **README.md**
  - [ ] Present ✅
  - [ ] Explains what the system does
  - [ ] Instructions to install and run
  - [ ] API endpoint examples
  - [ ] Project structure documented
  - [ ] Design decisions highlighted

- [ ] **.env.example**
  - [ ] Present ✅
  - [ ] Shows required environment variables
  - [ ] No actual secrets included

- [ ] **.gitignore**
  - [ ] Present ✅
  - [ ] Excludes `.env`, `__pycache__/`, `venv/`, etc.

### Git & Submission

- [ ] **Repository**
  - [ ] `git init` completed
  - [ ] `.gitignore` prevents secrets from being committed
  - [ ] All code files are committed
  - [ ] Commit messages are clear (e.g., "feat: add classifier", "docs: add README")

- [ ] **Final checks**
  - [ ] No API keys or secrets in codebase
  - [ ] All files are in the correct directory structure
  - [ ] README is readable on GitHub
  - [ ] Project folder name is `nistula-technical-assessment` (or similar)

---

## Quick Validation Script

```bash
#!/bin/bash
# Run this to validate your setup

echo "=== Checking file structure ==="
test -d src && echo "✓ src/ folder exists" || echo "✗ src/ folder missing"
test -d tests && echo "✓ tests/ folder exists" || echo "✗ tests/ folder missing"
test -f requirements.txt && echo "✓ requirements.txt exists" || echo "✗ requirements.txt missing"
test -f .env.example && echo "✓ .env.example exists" || echo "✗ .env.example missing"
test -f .gitignore && echo "✓ .gitignore exists" || echo "✗ .gitignore missing"
test -f schema.sql && echo "✓ schema.sql exists" || echo "✗ schema.sql missing"
test -f README.md && echo "✓ README.md exists" || echo "✗ README.md missing"
test -f thinking.md && echo "✓ thinking.md exists" || echo "✗ thinking.md missing"

echo ""
echo "=== Checking Python files ==="
test -f src/__init__.py && echo "✓ src/__init__.py exists" || echo "✗ src/__init__.py missing"
test -f src/main.py && echo "✓ src/main.py exists" || echo "✗ src/main.py missing"
test -f src/models.py && echo "✓ src/models.py exists" || echo "✗ src/models.py missing"
test -f src/classifier.py && echo "✓ src/classifier.py exists" || echo "✗ src/classifier.py missing"
test -f src/claude_client.py && echo "✓ src/claude_client.py exists" || echo "✗ src/claude_client.py missing"
test -f src/property_context.py && echo "✓ src/property_context.py exists" || echo "✗ src/property_context.py missing"
test -f tests/test_webhook.py && echo "✓ tests/test_webhook.py exists" || echo "✗ tests/test_webhook.py missing"

echo ""
echo "=== Checking Python syntax ==="
python -m py_compile src/main.py && echo "✓ src/main.py syntax OK" || echo "✗ src/main.py syntax error"
python -m py_compile src/models.py && echo "✓ src/models.py syntax OK" || echo "✗ src/models.py syntax error"
python -m py_compile src/classifier.py && echo "✓ src/classifier.py syntax OK" || echo "✗ src/classifier.py syntax error"

echo ""
echo "=== All checks complete ==="
```

---

## If You Get Stuck

### Error: `ModuleNotFoundError: No module named 'anthropic'`
```bash
pip install anthropic python-dotenv fastapi uvicorn pydantic
```

### Error: `ANTHROPIC_API_KEY not found`
```bash
# Create .env file:
echo "ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE" > .env
```

### Server won't start
```bash
# Make sure you're in the venv and uvicorn is installed
source venv/bin/activate
pip install uvicorn
uvicorn src.main:app --reload
```

### Tests fail
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/test_webhook.py -v
```

---

## Estimated Time to Completion

| Task | Time |
|------|------|
| Part 1 (FastAPI webhook) | 6–8 hours |
| Part 2 (PostgreSQL schema) | 1–2 hours |
| Part 3 (Thinking questions) | 1–2 hours |
| **Total** | **9–13 hours** |

---

## What to Submit

1. **GitHub repository URL** (or ZIP file)
   - Must include all files from this checklist
   - `.env` should NOT be committed (only `.env.example`)

2. **README** explaining what you built

3. **thinking.md** with your answers to Part 3

4. **(Optional)** A short video demo showing:
   - Server starting
   - Health endpoint responding
   - A test webhook call and the response
   - Swagger UI

---

Good luck! 🚀
