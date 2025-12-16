# DotEnvConfigFile

## Overview

**File Location:** `.env`  
**ConfigFile Class:** `DotEnvConfigFile`  
**File Type:** Environment variables (key=value format)  
**Priority:** Standard

A file for storing local environment variables like API keys and secrets. Automatically excluded from version control.

## Purpose

The `.env` file stores local configuration:

- **Secrets Management** - API keys, tokens, passwords
- **Environment-Specific Config** - Different values per environment
- **12-Factor App Compliance** - Separates config from code

### Why pyrig manages this file

pyrig creates an empty `.env` file to establish the pattern. The file is created during `pyrig init` but pyrig never modifies it - it's entirely user-managed.

## File Format

Environment variables use `KEY=value` format:

```bash
# Database
DATABASE_URL=postgresql://localhost:5432/mydb

# API keys
OPENAI_API_KEY=sk-...

# Feature flags
DEBUG=true
```

**Syntax:**
- No spaces around `=`
- Quotes optional (required for spaces)
- Comments with `#`
- No `export` keyword

## Default Configuration

Pyrig creates an empty file:

**File location:** `.env`

**File contents:**
```bash
[empty file]
```

## How to Use Environment Variables

### In Python Code

Use `python-dotenv` (included via `pyrig-dev`):

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

database_url = os.getenv("DATABASE_URL")
api_key = os.getenv("OPENAI_API_KEY")
```

### With uv run

Load `.env` explicitly with `--env-file`:

```bash
# Load .env file
uv run --env-file .env python my_script.py

# Or set UV_ENV_FILE environment variable
export UV_ENV_FILE=.env
uv run python my_script.py
```

## Best Practices

1. **Never commit `.env`** - Always in `.gitignore` (pyrig does this automatically)
2. **Use `.env.example`** - Create a template with dummy values to commit
3. **Document variables** - Add comments explaining each variable
4. **Rotate secrets** - Change secrets if accidentally exposed

## Related Files

- **`.gitignore`** - Excludes .env from version control ([gitignore.md](gitignore.md))

## Common Issues

### Issue: Variables not loading

**Cause:** `.env` file not loaded

**Solution:**
```python
from dotenv import load_dotenv
load_dotenv()  # Add this before accessing variables
```

### Issue: .env committed to git

**Cause:** Added before gitignore

**Solution:**
```bash
git rm --cached .env
git commit -m "Remove .env from version control"
```

## See Also

- [The Twelve-Factor App - Config](https://12factor.net/config)
- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
