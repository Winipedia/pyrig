# DotPythonVersionConfigFile

## Overview

**File Location:** `.python-version`
**ConfigFile Class:** `DotPythonVersionConfigFile`
**File Type:** Plain text (single line)
**Priority:** Standard

A single-line file containing the Python version to use for the project. This file is read by pyenv, asdf, uv, and other Python version managers to automatically activate the correct Python version when entering the project directory.

## Purpose

The `.python-version` file serves as the project's Python version specification:

- **Automatic Version Selection** - Tools like pyenv automatically switch to this version
- **Team Consistency** - Ensures all developers use the same Python version
- **CI/CD Alignment** - Can be used in workflows to match local development
- **Tool Integration** - Works with pyenv, asdf, uv, and other version managers

### Why pyrig manages this file

pyrig automatically derives the Python version from `pyproject.toml`:
1. **Single source of truth** - Version comes from `requires-python` in pyproject.toml
2. **Automatic synchronization** - Always matches the minimum supported version
3. **No manual updates** - Changes to `requires-python` automatically update this file
4. **Consistency guaranteed** - Development environment matches project requirements

The file is created during `pyrig init` and updated by `pyrig mkroot` whenever `requires-python` changes in `pyproject.toml`.

## File Contents

### Version String

- **Type:** String (Python version number)
- **Default:** Derived from `requires-python` in `pyproject.toml`
- **Required:** Yes
- **Purpose:** Specifies which Python version to use
- **Why pyrig sets it:** Uses the minimum supported version from `requires-python`

The version is in `major.minor` format (e.g., `3.12`, `3.13`). The patch version is omitted because version managers typically install the latest patch release for a given minor version.

### How the Version is Determined

pyrig extracts the version from `pyproject.toml`:

```toml
[project]
requires-python = ">=3.12"  # Minimum version is 3.12
```

The `.python-version` file will contain:
```
3.12
```

If `requires-python` is `">=3.13"`, the file will contain `3.13`.

## Default Configuration

For a project with `requires-python = ">=3.12"`:

**File location:** `.python-version`

**File contents:**
```
3.12
```

That's it - just the version number, nothing else.

## How Version Managers Use This File

### pyenv

When you `cd` into the project directory, pyenv automatically activates Python 3.12:

```bash
$ cd my-awesome-project
$ python --version
Python 3.12.7  # Automatically switched by pyenv
```

### asdf

Similar to pyenv, asdf reads `.python-version`:

```bash
$ cd my-awesome-project
$ asdf current python
python          3.12.7          /path/to/my-awesome-project/.python-version
```

### uv

uv uses `.python-version` when creating virtual environments:

```bash
$ uv venv
Using Python 3.12.7 from .python-version
Created virtual environment at .venv
```

### GitHub Actions

You can reference this file in workflows:

```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version-file: '.python-version'
```

## Relationship with pyproject.toml

The `.python-version` file is **derived from** `pyproject.toml`:

```toml
# pyproject.toml
[project]
requires-python = ">=3.12"  # Supports 3.12, 3.13, 3.14, etc.
```

```
# .python-version
3.12  # Uses the minimum supported version
```

**Why the minimum version?**
- **Compatibility testing** - Develop with the oldest supported version
- **Catches compatibility issues** - If it works on 3.12, it works on 3.13+
- **Conservative approach** - Ensures code doesn't use features from newer versions

## Customization

You can manually edit this file if you want to use a different Python version for development:

```bash
# Use Python 3.13 instead of 3.12
echo "3.13" > .python-version
```

**However**, be aware that:
- `pyrig mkroot` will reset it to the minimum version from `requires-python`
- Your local version should still satisfy `requires-python` constraints
- CI/CD may use a different version

### Recommended Approach

If you want to use a newer Python version for development:

1. **Update `pyproject.toml`** to support the new version:
   ```toml
   [project]
   requires-python = ">=3.13"  # Now minimum is 3.13
   ```

2. **Run `pyrig mkroot`** to update `.python-version`:
   ```bash
   uv run pyrig mkroot
   ```

3. **The file updates automatically**:
   ```
   3.13
   ```

This keeps everything synchronized.

## Related Files

- **`pyproject.toml`** - Source of truth for Python version requirements ([pyproject.toml](pyproject.md))
- **`.github/workflows/*.yaml`** - Workflows can reference this file for Python version
- **`uv.lock`** - Lock file may include Python version constraints

## Common Issues

### Issue: Version manager doesn't switch Python version

**Symptom:** `python --version` shows wrong version after `cd` into project

**Cause:** Version manager not installed or not configured

**Solution:**
1. **For pyenv:**
   ```bash
   # Install pyenv if not installed
   curl https://pyenv.run | bash

   # Add to shell config (~/.bashrc or ~/.zshrc)
   eval "$(pyenv init -)"

   # Install the required Python version
   pyenv install 3.12
   ```

2. **For asdf:**
   ```bash
   # Install asdf python plugin
   asdf plugin add python

   # Install the required Python version
   asdf install python 3.12
   ```

3. **For uv:**
   ```bash
   # uv automatically downloads Python versions
   uv venv  # Will use .python-version
   ```

### Issue: File contains wrong version

**Symptom:** `.python-version` shows `3.12` but you want `3.13`

**Cause:** The file is derived from `requires-python` in `pyproject.toml`

**Solution:**
Update `pyproject.toml` instead:
```toml
[project]
requires-python = ">=3.13"
```

Then run:
```bash
uv run pyrig mkroot
```

### Issue: File keeps getting reset

**Symptom:** You edit `.python-version` but it changes back

**Cause:** `pyrig mkroot` regenerates it from `pyproject.toml`

**Solution:**
Don't edit `.python-version` directly. Update `requires-python` in `pyproject.toml` instead.

### Issue: CI uses different Python version than local

**Symptom:** Tests pass locally but fail in CI with Python version errors

**Cause:** CI workflow specifies a different Python version

**Solution:**
Update your workflow to use `.python-version`:
```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version-file: '.python-version'
```

Or use a matrix to test multiple versions:
```yaml
strategy:
  matrix:
    python-version: ['3.12', '3.13', '3.14']
```

### Issue: Patch version mismatch

**Symptom:** File says `3.12` but you have `3.12.7` installed

**Cause:** This is normal and expected

**Solution:**
No action needed. Version managers install the latest patch release for the specified minor version. The file only specifies `major.minor`, and the version manager chooses the latest `major.minor.patch`.

## See Also

- [pyproject.toml](pyproject.md) - Source of Python version requirements
- [pyenv Documentation](https://github.com/pyenv/pyenv) - Python version manager
- [asdf Documentation](https://asdf-vm.com/) - Universal version manager
- [uv Documentation](https://docs.astral.sh/uv/) - Python package manager
- [PEP 440](https://peps.python.org/pep-0440/) - Version specifiers
- [Getting Started Guide](../getting-started.md) - Initial project setup


