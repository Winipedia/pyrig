# GitIgnoreConfigFile

## Overview

**File Location:** `.gitignore`
**ConfigFile Class:** `GitIgnoreConfigFile`
**File Type:** Plain text (gitignore patterns)
**Priority:** Standard

Specifies which files and directories Git should ignore and not track. Pyrig automatically generates a comprehensive `.gitignore` by combining GitHub's standard Python patterns with pyrig-specific additions.

## Purpose

The `.gitignore` file prevents unwanted files from being committed to version control:

- **Exclude Build Artifacts** - Compiled bytecode, distributions, eggs
- **Ignore Cache Directories** - `__pycache__`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`
- **Protect Secrets** - `.env` files with API keys and passwords
- **Skip IDE Files** - `.vscode/` and other editor-specific files
- **Omit Virtual Environments** - `.venv/`, `venv/`, `env/`

### Why pyrig manages this file

pyrig creates a comprehensive `.gitignore` to:
1. **Start clean** - Projects ignore the right files from day one
2. **Use industry standards** - Fetches GitHub's official Python.gitignore
3. **Add pyrig-specific patterns** - Includes `.experiment.py`, `.env`, and tool caches
4. **Prevent accidents** - Secrets and build artifacts never get committed
5. **Automatic updates** - New patterns are added when running `pyrig mkroot`

The file is created during `pyrig init` by fetching GitHub's Python.gitignore and adding pyrig-specific patterns. Running `pyrig mkroot` adds any new patterns without removing your custom additions.

## File Structure

The `.gitignore` file is organized into sections:

### 1. GitHub's Standard Python Patterns

Fetched from: `https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore`

Includes patterns for:
- Byte-compiled files (`__pycache__/`, `*.pyc`)
- Distribution/packaging (`dist/`, `*.egg-info/`)
- Testing/coverage (`htmlcov/`, `.coverage`)
- Virtual environments (`.venv/`, `venv/`)
- Framework-specific files (Django, Flask, Jupyter)
- IDE files (PyCharm, VS Code)

### 2. VS Code Workspace Files

```gitignore
# vscode stuff
.vscode/
```

### 3. Pyrig-Specific Patterns

```gitignore
# pyrig stuff
.git/
.experiment.py
```

### 4. Additional Tool Caches

```gitignore
# others
.env
.mypy_cache/
.pytest_cache/
.ruff_cache/
.venv/
dist/
```

## Pattern Syntax

### Basic Patterns

```gitignore
# Ignore a specific file
secret.txt

# Ignore all files with extension
*.log

# Ignore a directory
__pycache__/

# Ignore files in any directory
**/temp.txt
```

### Advanced Patterns

```gitignore
# Ignore everything in a directory except one file
build/*
!build/README.md

# Ignore files only in root
/config.local.py

# Ignore files in specific subdirectory
tests/fixtures/*.json

# Character ranges
*.[oa]  # Matches *.o and *.a
```

### Negation

```gitignore
# Ignore all .txt files
*.txt

# Except this one
!important.txt
```

## Default Configuration

Here's what pyrig generates (abbreviated for clarity):

**File location:** `.gitignore`

**File contents:**
```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[codz]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py.cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff
instance/
.webassets-cache

# Scrapy stuff
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# Environments
.env
.envrc
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# Ruff
.ruff_cache/

# PyPI configuration
.pypirc

# vscode stuff
.vscode/

# pyrig stuff
.git/
.experiment.py

# others
.env
.mypy_cache/
.pytest_cache/
.ruff_cache/
.venv/
dist/
```

## Key Patterns Explained

### Python Bytecode

```gitignore
__pycache__/
*.py[codz]
*$py.class
```

- **Why:** Bytecode is generated automatically and platform-specific
- **Impact:** Reduces repo size, prevents conflicts

### Distribution Files

```gitignore
dist/
build/
*.egg-info/
```

- **Why:** Build artifacts should be generated, not committed
- **Impact:** Keeps repo clean, forces proper builds

### Virtual Environments

```gitignore
.venv/
venv/
env/
ENV/
```

- **Why:** Virtual environments are local and large
- **Impact:** Each developer creates their own venv

### Secrets

```gitignore
.env
.envrc
```

- **Why:** Prevents committing API keys and passwords
- **Impact:** Critical security protection

### Tool Caches

```gitignore
.mypy_cache/
.pytest_cache/
.ruff_cache/
.coverage
```

- **Why:** Caches are local and regenerated automatically
- **Impact:** Reduces repo size and merge conflicts

### IDE Files

```gitignore
.vscode/
.idea/
*.swp
```

- **Why:** IDE settings are personal preferences
- **Impact:** Prevents conflicts between developers using different editors

### Pyrig-Specific

```gitignore
.experiment.py
```

- **Why:** Temporary experimentation file (see [dotexperiment.md](dotexperiment.md))
- **Impact:** Allows safe experimentation without committing

## How Pyrig Updates .gitignore

### Initial Creation

When you run `pyrig init`:

1. **Fetch GitHub's Python.gitignore** - Gets the latest standard patterns
2. **Add pyrig patterns** - Appends pyrig-specific patterns
3. **Write to .gitignore** - Creates the file

### Subsequent Updates

When you run `pyrig mkroot`:

1. **Load existing patterns** - Reads your current .gitignore
2. **Fetch latest GitHub patterns** - Gets any new standard patterns
3. **Add missing patterns** - Appends only patterns you don't have
4. **Preserve custom patterns** - Never removes your additions

This means you can safely add your own patterns - they won't be removed.

## Customization

You can freely add your own patterns to `.gitignore`. Pyrig will preserve them.

### Adding Project-Specific Patterns

```gitignore
# Add at the end of .gitignore

# Project-specific
data/raw/
models/checkpoints/
*.pkl
*.h5

# Local configuration
config.local.yaml
secrets.json
```

### Adding Framework-Specific Patterns

**For Django:**
```gitignore
# Django
media/
staticfiles/
local_settings.py
```

**For FastAPI:**
```gitignore
# FastAPI
.pytest_cache/
.coverage
htmlcov/
```

**For Data Science:**
```gitignore
# Data Science
*.ipynb_checkpoints
*.csv
*.parquet
data/
models/
```

### Global vs Local .gitignore

**Local .gitignore** (this file):
- Project-specific patterns
- Committed to the repository
- Shared with all developers

**Global .gitignore** (`~/.gitignore_global`):
- Personal patterns (OS files, editor files)
- Not committed
- Applies to all your repositories

**Setup global gitignore:**
```bash
# Create global gitignore
cat > ~/.gitignore_global << EOF
# macOS
.DS_Store
.AppleDouble
.LSOverride

# Windows
Thumbs.db
Desktop.ini

# Linux
*~
.directory

# Personal
scratch/
notes.txt
EOF

# Configure git to use it
git config --global core.excludesfile ~/.gitignore_global
```

## Checking if a File is Ignored

### Using git check-ignore

```bash
# Check if a file is ignored
git check-ignore .env
# Output: .env (means it's ignored)

# Check with verbose output
git check-ignore -v .env
# Output: .gitignore:151:.env    .env

# Check multiple files
git check-ignore .env dist/ __pycache__/
```

### Using Pyrig's API

```python
from pyrig.dev.configs.git.gitignore import GitIgnoreConfigFile

# Check if a path is ignored
is_ignored = GitIgnoreConfigFile.path_is_in_gitignore(".env")
print(is_ignored)  # True

is_ignored = GitIgnoreConfigFile.path_is_in_gitignore("my_script.py")
print(is_ignored)  # False
```

## Common Patterns by Use Case

### Web Application

```gitignore
# Static files
staticfiles/
media/

# Database
*.db
*.sqlite3
db.sqlite3-journal

# Logs
logs/
*.log

# Uploads
uploads/
```

### CLI Tool

```gitignore
# Build artifacts
dist/
build/
*.spec

# User data
~/.my-tool/
*.cache
```

### Library/Package

```gitignore
# Distribution
dist/
build/
*.egg-info/

# Documentation builds
docs/_build/
docs/_static/
docs/_templates/
```

### Data Science

```gitignore
# Data
data/raw/
data/processed/
*.csv
*.parquet
*.feather

# Models
models/
checkpoints/
*.pkl
*.h5
*.pth

# Notebooks
.ipynb_checkpoints/
*-checkpoint.ipynb

# Experiments
mlruns/
wandb/
```

## Related Files

- **`.env`** - Secrets file that's gitignored ([dotenv.md](dotenv.md))
- **`.experiment.py`** - Temporary file that's gitignored ([dotexperiment.md](dotexperiment.md))
- **`.git/`** - Git directory (gitignored to prevent nested repos)

## Common Issues

### Issue: File is tracked but should be ignored

**Symptom:** File appears in `git status` even though it's in `.gitignore`

**Cause:** File was tracked before being added to `.gitignore`

**Solution:**
```bash
# Remove from tracking (keeps local file)
git rm --cached path/to/file

# Commit the removal
git commit -m "Stop tracking file"

# Now it's ignored
git status  # File won't appear
```

### Issue: Accidentally committed secrets

**Symptom:** `.env` file with secrets is in git history

**Cause:** File was committed before `.gitignore` was created

**Solution:**
1. **Immediately rotate all secrets** - They're now public
2. **Remove from git:**
   ```bash
   git rm --cached .env
   git commit -m "Remove .env from tracking"
   ```
3. **Remove from history:**
   ```bash
   # Use git filter-branch or BFG Repo-Cleaner
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all

   # Force push
   git push origin --force --all
   ```

### Issue: .gitignore not working

**Symptom:** Patterns don't seem to work

**Cause:** Various reasons

**Solutions:**

**1. Check pattern syntax:**
```bash
# Test pattern
git check-ignore -v path/to/file
```

**2. Clear git cache:**
```bash
# Sometimes git caches need clearing
git rm -r --cached .
git add .
git commit -m "Fix gitignore"
```

**3. Check for negation:**
```gitignore
# If you have this:
*.txt
!important.txt

# But important.txt is in a directory that's ignored:
temp/  # This ignores temp/ and everything in it
# Then !important.txt won't work for temp/important.txt
```

### Issue: Want to ignore all files except specific ones

**Symptom:** Need to ignore a directory but keep one file

**Cause:** Negation patterns needed

**Solution:**
```gitignore
# Ignore everything in data/
data/*

# Except README
!data/README.md

# Except .gitkeep files
!data/.gitkeep
!data/**/.gitkeep
```

### Issue: Pattern too broad

**Symptom:** Ignoring files you want to track

**Cause:** Pattern matches more than intended

**Solution:**
```gitignore
# Too broad
*.json  # Ignores ALL json files

# More specific
config/*.json  # Only config directory
!package.json  # Except package.json
```

### Issue: .gitignore changes not taking effect

**Symptom:** Added pattern but files still tracked

**Cause:** Files were already tracked

**Solution:**
```bash
# Untrack all files matching new pattern
git rm -r --cached .
git add .
git commit -m "Apply new gitignore rules"
```

### Issue: Want to commit an ignored file once

**Symptom:** Need to commit a file that matches .gitignore

**Cause:** Sometimes you need to commit an exception

**Solution:**
```bash
# Force add an ignored file
git add -f path/to/ignored/file

# Or use negation in .gitignore
!path/to/specific/file
```

## Best Practices

### ✅ DO

- **Commit .gitignore early** - Before committing any code
- **Use specific patterns** - `config/*.json` not `*.json`
- **Add comments** - Explain why patterns exist
- **Test patterns** - Use `git check-ignore -v`
- **Keep it organized** - Group related patterns
- **Use .env.example** - For environment variable templates

### ❌ DON'T

- **Don't ignore .gitignore** - It should be committed
- **Don't ignore too broadly** - Be specific
- **Don't commit then ignore** - Ignore before committing
- **Don't ignore source code** - Only ignore generated files
- **Don't ignore lock files** - `uv.lock` should be committed

## See Also

- [GitHub's gitignore Templates](https://github.com/github/gitignore) - Official templates
- [gitignore.io](https://www.toptal.com/developers/gitignore) - Generate .gitignore files
- [Git Documentation - gitignore](https://git-scm.com/docs/gitignore) - Official git docs
- [.env](dotenv.md) - Environment variables file
- [.experiment.py](dotexperiment.md) - Temporary experimentation file
- [Getting Started Guide](../getting-started.md) - Initial project setup


