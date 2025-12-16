# ZeroTestConfigFile

## Overview

**File Location:** `tests/test_zero.py`
**ConfigFile Class:** `ZeroTestConfigFile`
**File Type:** Python
**Priority:** Standard

A placeholder test file that ensures pytest runs successfully even when no other tests have been written. This allows fixture initialization and validation to occur from day one.

## Purpose

The `tests/test_zero.py` file serves as a minimal test:

- **Pytest Success** - Ensures `pytest` exits with code 0 (success)
- **Fixture Execution** - Triggers fixture setup/teardown even with no real tests
- **CI Validation** - Allows CI to pass before tests are written
- **Development Placeholder** - Provides a starting point for test development
- **Coverage Baseline** - Establishes 0% coverage baseline

### Why pyrig manages this file

pyrig creates `test_zero.py` to:
1. **Immediate success** - `pytest` works from day one
2. **Fixture validation** - Ensures conftest.py and fixtures load correctly
3. **CI readiness** - GitHub Actions health check passes
4. **No false failures** - Empty test suite doesn't fail
5. **Delete when ready** - Remove once you write real tests

The file is created during `pyrig init`. You can delete it once you have other tests.

## File Structure

### Docstring

```python
"""Contains an empty test."""
```

- **Purpose:** Describes the file's minimal nature

### test_zero Function

```python
def test_zero() -> None:
    """Empty test.

    Exists so that when no tests are written yet the base fixtures are executed.
    """
```

- **Type:** Test function (pytest discovers functions starting with `test_`)
- **Default:** Empty function body
- **Required:** Yes (for the file to be a valid test)
- **Purpose:** Provides a passing test
- **Why pyrig sets it:** Ensures pytest has at least one test to run

**How it works:**
1. Pytest discovers `test_zero.py`
2. Finds `test_zero()` function
3. Runs the function (does nothing)
4. Test passes (no assertions, no errors)
5. Pytest exits with code 0 (success)

## Default Configuration

For a project named `my-awesome-project`:

**File location:** `tests/test_zero.py`

**File contents:**
```python
"""Contains an empty test."""


def test_zero() -> None:
    """Empty test.

    Exists so that when no tests are written yet the base fixtures are executed.
    """
```

## Why This Matters

### Without test_zero.py

```bash
# No tests exist
$ uv run pytest
collected 0 items

# Pytest exits with code 5 (no tests collected)
$ echo $?
5
```

**Problems:**
- CI fails (non-zero exit code)
- Fixtures never execute
- Can't validate test infrastructure
- Confusing for new projects

### With test_zero.py

```bash
# One test exists
$ uv run pytest
collected 1 item

tests/test_zero.py .                                                     [100%]

============================== 1 passed in 0.01s ===============================

# Pytest exits with code 0 (success)
$ echo $?
0
```

**Benefits:**
- CI passes
- Fixtures execute and validate
- Test infrastructure confirmed working
- Clear starting point

## When to Delete

You can safely delete `test_zero.py` once you have other tests:

```bash
# Check if you have other tests
ls tests/test_*.py
# tests/test_main.py  tests/test_my_module.py  tests/test_zero.py

# If you have other tests, delete test_zero.py
rm tests/test_zero.py

# Verify tests still pass
uv run pytest
```

**When to keep it:**
- You haven't written any tests yet
- You want to ensure fixtures always execute
- You prefer having a baseline test

**When to delete it:**
- You have real tests
- You want accurate coverage metrics
- You find it confusing

## Fixture Execution

Even though `test_zero()` is empty, pytest still:

1. **Loads conftest.py** - Imports all fixtures
2. **Runs autouse fixtures** - Fixtures with `autouse=True`
3. **Validates fixture definitions** - Catches syntax errors
4. **Executes setup/teardown** - For session/module scoped fixtures

This means `test_zero.py` validates your test infrastructure.

## Customization

You can modify `test_zero.py` to do basic validation:

### Example: Validate Imports

```python
"""Contains an empty test."""


def test_zero() -> None:
    """Empty test that validates imports."""
    # Ensure package imports successfully
    import my_awesome_project

    # Ensure main module exists
    from my_awesome_project import main

    # Test passes if imports succeed
```

### Example: Validate Configuration

```python
"""Contains an empty test."""

import os


def test_zero() -> None:
    """Empty test that validates environment."""
    # Ensure Python version is correct
    import sys
    assert sys.version_info >= (3, 12)

    # Ensure package is installed
    import my_awesome_project
    assert my_awesome_project.__name__ == "my_awesome_project"
```

### Example: Use Fixtures

```python
"""Contains an empty test."""


def test_zero(config_file_factory) -> None:
    """Empty test that validates fixtures."""
    # Ensure config_file_factory works
    from pyrig.dev.configs.pyproject import PyprojectConfigFile

    TestConfig = config_file_factory(PyprojectConfigFile)
    assert TestConfig is not None
```

**Note:** Pyrig will preserve modifications as long as the file contains `def test_zero`.

## Related Files

- **`tests/conftest.py`** - Pytest configuration and fixtures ([conftest.md](conftest.md))
- **`tests/test_main.py`** - Main entry point test ([main-test.md](main-test.md))
- **`tests/fixtures.py`** - Custom fixtures ([fixtures-init.md](fixtures-init.md))
- **`pyproject.toml`** - Pytest configuration ([pyproject.toml](pyproject.md))

## Common Issues

### Issue: test_zero.py affects coverage

**Symptom:** Coverage shows 0% for test_zero.py

**Cause:** Coverage includes test files

**Solution:**
```toml
# pyproject.toml
[tool.coverage.run]
omit = [
    "tests/*",
]
```

Or delete `test_zero.py` once you have real tests.

### Issue: Want to skip test_zero.py

**Symptom:** Don't want test_zero to run

**Cause:** Pytest discovers all test_* files

**Solution:**
```bash
# Skip specific test
uv run pytest --ignore=tests/test_zero.py

# Or delete it
rm tests/test_zero.py
```

### Issue: test_zero.py fails

**Symptom:** Empty test fails

**Cause:** Fixture or import error

**Solution:**
```bash
# Run with verbose output
uv run pytest tests/test_zero.py -v

# Check for fixture errors
uv run pytest tests/test_zero.py --setup-show
```

The failure indicates a problem with your test infrastructure, not the test itself.

### Issue: Pytest still collects 0 items

**Symptom:** Pytest doesn't find test_zero.py

**Cause:** File not in tests directory or wrong naming

**Solution:**
```bash
# Ensure file exists
ls tests/test_zero.py

# Ensure it's named correctly (test_*.py or *_test.py)
# Ensure it's in the tests directory

# Run pytest with discovery info
uv run pytest --collect-only
```

## Best Practices

### ✅ DO

- **Keep it simple** - Empty test is fine
- **Delete when ready** - Remove once you have real tests
- **Use for validation** - Can add basic import checks
- **Understand its purpose** - It's a placeholder

### ❌ DON'T

- **Don't write real tests here** - Create separate test files
- **Don't rely on it long-term** - It's a starting point
- **Don't skip it in CI** - It validates test infrastructure
- **Don't make it complex** - Keep it minimal

## See Also

- [pytest Documentation](https://docs.pytest.org/) - Official pytest docs
- [pytest Test Discovery](https://docs.pytest.org/en/stable/goodpractices.html#test-discovery) - How pytest finds tests
- [conftest.py](conftest.md) - Pytest configuration
- [test_main.py](main-test.md) - Main entry point test
- [Getting Started Guide](../getting-started.md) - Initial project setup


