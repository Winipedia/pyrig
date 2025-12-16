# PreCommitConfigConfigFile

## Overview

**File Location:** `.pre-commit-config.yaml`
**ConfigFile Class:** `PreCommitConfigConfigFile`
**File Type:** YAML
**Priority:** Standard

Configures pre-commit hooks that automatically run code quality checks before each git commit. Pyrig sets up local hooks for linting (ruff), formatting (ruff), type checking (mypy + ty), and security scanning (bandit).

## Purpose

The `.pre-commit-config.yaml` file enforces code quality standards automatically:

- **Prevent Bad Commits** - Catches issues before they enter version control
- **Enforce Standards** - Runs linting, formatting, and type checking automatically
- **Security Scanning** - Detects security vulnerabilities with bandit
- **Fast Feedback** - Developers see issues immediately, not in CI
- **Consistent Quality** - All commits meet the same standards

### Why pyrig manages this file

pyrig configures pre-commit hooks to:
1. **Automatic enforcement** - Quality checks run without manual intervention
2. **Local-first** - Uses `language: system` to run tools from your environment
3. **Comprehensive checks** - Linting, formatting, type checking, and security
4. **Always run** - Checks all files on every commit for consistency
5. **CI alignment** - Same checks run locally and in GitHub Actions

The file is created during `pyrig init` and hooks are installed automatically. Running `pyrig mkroot` updates the configuration if needed.

## Pre-Commit Framework

### What is pre-commit?

[pre-commit](https://pre-commit.com/) is a framework for managing git hooks. It:
- Runs scripts before commits
- Supports multiple languages and tools
- Can fetch hooks from remote repositories
- Provides a consistent interface

### Local vs Remote Hooks

**Remote hooks** (typical pre-commit usage):
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
```

**Local hooks** (pyrig's approach):
```yaml
repos:
  - repo: local
    hooks:
      - id: lint-code
        entry: ruff check --fix
        language: system
```

**Why pyrig uses local hooks:**
- **Uses your environment** - Same versions as in `pyproject.toml`
- **Faster** - No remote fetching or separate environments
- **Consistent** - Matches CI exactly
- **Simpler** - One source of truth for tool versions

## Configuration Structure

### Top-Level Configuration

#### `repos`

- **Type:** Array of repository configurations
- **Default:** Single local repository
- **Required:** Yes
- **Purpose:** Defines where hooks come from
- **Why pyrig sets it:** Uses `repo: local` to run tools from your environment

### Repository Configuration

#### `repo`

- **Type:** String
- **Default:** `"local"`
- **Required:** Yes
- **Purpose:** Specifies the hook source
- **Why pyrig sets it:** `"local"` means hooks run from your installed tools

#### `hooks`

- **Type:** Array of hook configurations
- **Default:** 5 hooks (lint, format, type check, static type check, security)
- **Required:** Yes
- **Purpose:** Defines which checks to run
- **Why pyrig sets it:** Comprehensive quality checks

## Hook Configurations

### 1. lint-code

```yaml
- id: lint-code
  name: lint-code
  entry: ruff check --fix
  language: system
  always_run: true
  pass_filenames: false
```

- **Purpose:** Lint Python code and auto-fix issues
- **Tool:** ruff with ALL rules enabled
- **Auto-fix:** Yes (`--fix` flag)
- **When:** Every commit, all files

### 2. format-code

```yaml
- id: format-code
  name: format-code
  entry: ruff format
  language: system
  always_run: true
  pass_filenames: false
```

- **Purpose:** Format Python code consistently
- **Tool:** ruff formatter (Black-compatible)
- **Auto-fix:** Yes (formats in place)
- **When:** Every commit, all files

### 3. check-types

```yaml
- id: check-types
  name: check-types
  entry: ty check
  language: system
  always_run: true
  pass_filenames: false
```

- **Purpose:** Runtime type checking with ty
- **Tool:** ty (pyrig's type checker)
- **Auto-fix:** No (reports errors)
- **When:** Every commit, all files

### 4. check-static-types

```yaml
- id: check-static-types
  name: check-static-types
  entry: mypy --exclude-gitignore
  language: system
  always_run: true
  pass_filenames: false
```

- **Purpose:** Static type checking
- **Tool:** mypy in strict mode
- **Auto-fix:** No (reports errors)
- **When:** Every commit, all files
- **Note:** Excludes gitignored files

### 5. check-security

```yaml
- id: check-security
  name: check-security
  entry: bandit -c pyproject.toml -r .
  language: system
  always_run: true
  pass_filenames: false
```

- **Purpose:** Security vulnerability scanning
- **Tool:** bandit
- **Auto-fix:** No (reports vulnerabilities)
- **When:** Every commit, all files
- **Config:** Uses `pyproject.toml` for bandit settings

## Hook Options Explained

### `id`

- **Type:** String
- **Purpose:** Unique identifier for the hook
- **Example:** `"lint-code"`

### `name`

- **Type:** String
- **Purpose:** Display name shown during execution
- **Example:** `"lint-code"`

### `entry`

- **Type:** String (shell command)
- **Purpose:** Command to execute
- **Example:** `"ruff check --fix"`

### `language`

- **Type:** String
- **Default:** `"system"`
- **Purpose:** How to run the hook
- **Why `system`:** Uses tools from your environment (uv-managed)

### `always_run`

- **Type:** Boolean
- **Default:** `true`
- **Purpose:** Run even if no files match
- **Why `true`:** Ensures all files are checked every commit

### `pass_filenames`

- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Whether to pass changed filenames to the command
- **Why `false`:** We check all files, not just changed ones

## Default Configuration

For a project named `my-awesome-project`:

**File location:** `.pre-commit-config.yaml`

**File contents:**
```yaml
repos:
- repo: local
  hooks:
  - id: lint-code
    name: lint-code
    entry: ruff check --fix
    language: system
    always_run: true
    pass_filenames: false
  - id: format-code
    name: format-code
    entry: ruff format
    language: system
    always_run: true
    pass_filenames: false
  - id: check-types
    name: check-types
    entry: ty check
    language: system
    always_run: true
    pass_filenames: false
  - id: check-static-types
    name: check-static-types
    entry: mypy --exclude-gitignore
    language: system
    always_run: true
    pass_filenames: false
  - id: check-security
    name: check-security
    entry: bandit -c pyproject.toml -r .
    language: system
    always_run: true
    pass_filenames: false
```

## Installation and Usage

### Installing Hooks

Pre-commit hooks must be installed into your git repository:

```bash
# Install hooks (done automatically by pyrig init)
uv run pre-commit install

# This creates .git/hooks/pre-commit
```

After installation, hooks run automatically on `git commit`.

### Running Hooks Manually

```bash
# Run all hooks on all files
uv run pre-commit run --all-files

# Run all hooks on staged files only
uv run pre-commit run

# Run a specific hook
uv run pre-commit run lint-code

# Run with verbose output
uv run pre-commit run --all-files --verbose
```

### Using Pyrig's Helper

```python
from pyrig.dev.configs.git.pre_commit import PreCommitConfigConfigFile

# Install hooks
PreCommitConfigConfigFile.install()

# Run all hooks
PreCommitConfigConfigFile.run_hooks()

# Run without installing first
PreCommitConfigConfigFile.run_hooks(with_install=False)

# Run on staged files only
PreCommitConfigConfigFile.run_hooks(all_files=False)
```

### Bypassing Hooks

Sometimes you need to commit without running hooks:

```bash
# Skip all hooks
git commit --no-verify -m "WIP: temporary commit"

# Or use the short form
git commit -n -m "WIP: temporary commit"
```

**Warning:** Only bypass hooks when absolutely necessary. CI will still run the checks.

## Execution Flow

### What Happens on Commit

1. **You run:** `git commit -m "Add feature"`
2. **Pre-commit activates:** Reads `.pre-commit-config.yaml`
3. **Runs each hook in order:**
   - `lint-code` - Fixes linting issues
   - `format-code` - Formats code
   - `check-types` - Checks runtime types
   - `check-static-types` - Checks static types
   - `check-security` - Scans for vulnerabilities
4. **If all pass:** Commit succeeds
5. **If any fail:** Commit is blocked, you fix issues and try again

### Hook Execution Order

Hooks run sequentially in the order defined:

1. **lint-code** (auto-fixes)
2. **format-code** (auto-fixes)
3. **check-types** (reports errors)
4. **check-static-types** (reports errors)
5. **check-security** (reports errors)

**Why this order:**
- Linting and formatting first (they auto-fix)
- Type checking after (on clean code)
- Security last (comprehensive scan)

## Customization

You can customize pre-commit hooks by subclassing or editing the file.

### Adding a New Hook

**Option 1: Edit .pre-commit-config.yaml**

```yaml
repos:
- repo: local
  hooks:
  # ... existing hooks ...
  - id: check-docstrings
    name: check-docstrings
    entry: pydocstyle
    language: system
    always_run: true
    pass_filenames: false
```

**Option 2: Subclass PreCommitConfigConfigFile**

```python
from pyrig.dev.configs.git.pre_commit import PreCommitConfigConfigFile


class CustomPreCommitConfigFile(PreCommitConfigConfigFile):
    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Add custom hooks."""
        config = super().get_configs()

        # Add a new hook
        new_hook = cls.get_hook(
            "check-docstrings",
            ["pydocstyle"],
        )
        config["repos"][0]["hooks"].append(new_hook)

        return config
```

### Removing a Hook

**Edit .pre-commit-config.yaml:**

```yaml
repos:
- repo: local
  hooks:
  - id: lint-code
    name: lint-code
    entry: ruff check --fix
    language: system
    always_run: true
    pass_filenames: false
  - id: format-code
    name: format-code
    entry: ruff format
    language: system
    always_run: true
    pass_filenames: false
  # Removed check-types, check-static-types, check-security
```

**Note:** Pyrig will add them back on `pyrig mkroot`. To permanently remove, subclass and override `get_configs()`.

### Modifying Hook Behavior

**Example: Run hooks only on changed files**

```yaml
- id: lint-code
  name: lint-code
  entry: ruff check --fix
  language: system
  always_run: false  # Changed from true
  pass_filenames: true  # Changed from false
  types: [python]  # Added: only Python files
```

**Example: Add arguments to a hook**

```yaml
- id: check-static-types
  name: check-static-types
  entry: mypy --exclude-gitignore --strict
  language: system
  always_run: true
  pass_filenames: false
```

### Using Remote Hooks

You can add remote hooks alongside local ones:

```yaml
repos:
- repo: local
  hooks:
  # ... pyrig's local hooks ...

- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
  - id: trailing-whitespace
  - id: end-of-file-fixer
  - id: check-yaml
  - id: check-added-large-files
```

## Integration with CI

Pre-commit hooks run the same checks as GitHub Actions:

### Local (Pre-Commit)

```yaml
# .pre-commit-config.yaml
- id: lint-code
  entry: ruff check --fix
```

### CI (GitHub Actions)

```yaml
# .github/workflows/health-check.yaml
- name: Lint code
  run: uv run ruff check --fix
```

**Benefits:**
- Catch issues before pushing
- Faster feedback loop
- Reduced CI failures
- Same tools, same results

## Related Files

- **`pyproject.toml`** - Configuration for ruff, mypy, bandit ([pyproject.toml](pyproject.md))
- **`.github/workflows/health-check.yaml`** - CI runs same checks ([health-check-workflow.md](health-check-workflow.md))
- **`.gitignore`** - Excludes `.pre-commit-config.yaml` cache files ([gitignore.md](gitignore.md))

## Common Issues

### Issue: Hooks not running on commit

**Symptom:** `git commit` doesn't trigger pre-commit

**Cause:** Hooks not installed

**Solution:**
```bash
# Install hooks
uv run pre-commit install

# Verify installation
ls .git/hooks/pre-commit
```

### Issue: Hook fails with "command not found"

**Symptom:** `ruff: command not found` or similar

**Cause:** Tool not installed in environment

**Solution:**
```bash
# Sync dependencies
uv sync

# Verify tool is available
uv run ruff --version
uv run mypy --version
uv run bandit --version
```

### Issue: Hooks are too slow

**Symptom:** Commits take a long time

**Cause:** Running on all files every time

**Solution:**

**Option 1: Run on changed files only**
```yaml
- id: lint-code
  entry: ruff check --fix
  always_run: false
  pass_filenames: true
  types: [python]
```

**Option 2: Skip some hooks locally**
```bash
# Set environment variable
export SKIP=check-security,check-static-types

# Or per-commit
SKIP=check-security git commit -m "Quick fix"
```

**Option 3: Use faster tools**
- Ruff is already very fast
- Consider removing bandit if security scans are slow

### Issue: Hook modifies files but commit still fails

**Symptom:** `lint-code` or `format-code` fixes files but commit is rejected

**Cause:** Pre-commit detects file modifications

**Solution:**
```bash
# Stage the auto-fixed files
git add -u

# Commit again
git commit -m "Your message"
```

**Or configure hooks to auto-stage:**
```yaml
- id: lint-code
  entry: ruff check --fix
  stages: [commit]
  # Add this to auto-stage changes:
  # (requires pre-commit 2.x+)
```

### Issue: Want to run hooks in CI only

**Symptom:** Don't want local pre-commit hooks

**Cause:** Personal preference

**Solution:**
```bash
# Uninstall hooks
uv run pre-commit uninstall

# Hooks won't run locally but CI still checks
```

### Issue: Hooks fail on merge commits

**Symptom:** Pre-commit fails during `git merge`

**Cause:** Merge conflicts or combined changes

**Solution:**
```bash
# Skip hooks for merge commit
git merge --no-verify branch-name

# Or fix issues and commit
git add -u
git commit --no-edit
```

### Issue: Different results locally vs CI

**Symptom:** Pre-commit passes but CI fails

**Cause:** Different tool versions or configurations

**Solution:**
```bash
# Ensure dependencies are synced
uv sync

# Run the exact CI commands locally
uv run ruff check --fix
uv run ruff format
uv run mypy --exclude-gitignore
uv run bandit -c pyproject.toml -r .

# Check tool versions match pyproject.toml
uv run ruff --version
```

### Issue: Want to auto-update hook versions

**Symptom:** Using remote hooks with outdated versions

**Cause:** Manual version management

**Solution:**
```bash
# Auto-update remote hook versions
uv run pre-commit autoupdate

# This updates the 'rev' field in .pre-commit-config.yaml
```

**Note:** Pyrig uses local hooks, so this doesn't apply to the default configuration.

## Best Practices

### ✅ DO

- **Install hooks early** - Run `pre-commit install` after cloning
- **Run manually before pushing** - `pre-commit run --all-files`
- **Keep tools updated** - Sync dependencies regularly
- **Fix issues immediately** - Don't bypass hooks habitually
- **Use same tools in CI** - Consistency is key

### ❌ DON'T

- **Don't bypass hooks regularly** - They exist for a reason
- **Don't ignore failures** - Fix the issues
- **Don't use different tool versions** - Keep local and CI in sync
- **Don't add too many hooks** - Keep commits fast
- **Don't run expensive operations** - Save those for CI

## Advanced Usage

### Running Hooks in CI

You can run pre-commit in GitHub Actions:

```yaml
# .github/workflows/health-check.yaml
- name: Run pre-commit
  run: |
    uv run pre-commit install
    uv run pre-commit run --all-files
```

**Note:** Pyrig runs individual tools instead for better control and caching.

### Hook Stages

Pre-commit supports different stages:

```yaml
- id: lint-code
  entry: ruff check --fix
  stages: [commit, push, manual]
```

**Stages:**
- `commit` - Run on `git commit`
- `push` - Run on `git push`
- `manual` - Only when explicitly run
- `merge-commit` - Run on merge commits
- `prepare-commit-msg` - Modify commit message

### Passing Arguments to Hooks

```bash
# Pass arguments to a specific hook
uv run pre-commit run lint-code -- --verbose

# Pass files to check
uv run pre-commit run --files src/my_module.py
```

### Creating Custom Hooks

```yaml
- id: custom-check
  name: Custom validation
  entry: python scripts/validate.py
  language: system
  always_run: true
  pass_filenames: false
```

## See Also

- [pre-commit Documentation](https://pre-commit.com/) - Official pre-commit docs
- [pre-commit Hooks](https://github.com/pre-commit/pre-commit-hooks) - Common hooks
- [Ruff](https://docs.astral.sh/ruff/) - Linter and formatter
- [mypy](https://mypy.readthedocs.io/) - Static type checker
- [bandit](https://bandit.readthedocs.io/) - Security scanner
- [pyproject.toml](pyproject.md) - Tool configuration
- [Health Check Workflow](health-check-workflow.md) - CI checks
- [Getting Started Guide](../getting-started.md) - Initial project setup


