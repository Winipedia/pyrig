# MainTestConfigFile

## Overview

**File Location:** `tests/test_{package_name}/test_main.py`
**ConfigFile Class:** `MainTestConfigFile`
**File Type:** Python
**Priority:** Standard

Tests the CLI entry point by verifying that `--help` works correctly. This ensures your application's main function is properly configured and callable from the command line.

## Purpose

The `tests/test_{package_name}/test_main.py` file validates the CLI:

- **Entry Point Validation** - Ensures CLI is properly configured
- **Help Command** - Verifies `--help` works
- **Import Check** - Confirms main module imports successfully
- **Integration Test** - Tests the full CLI invocation path
- **CI Validation** - Catches CLI configuration issues early

### Why pyrig manages this file

pyrig creates `test_main.py` to:
1. **Immediate validation** - CLI works from day one
2. **Catch configuration errors** - Detects issues in `pyproject.toml` scripts
3. **Integration testing** - Tests the full command-line interface
4. **Best practices** - Every CLI should respond to `--help`
5. **CI readiness** - Ensures deployable CLI

The file is created during `pyrig init` in the test directory mirroring your package structure.

## File Location

The file is placed in a test directory that mirrors your package structure:

```
my-awesome-project/
├── my_awesome_project/
│   └── main.py
└── tests/
    └── test_my_awesome_project/
        └── test_main.py  # <-- Here
```

This follows pytest's convention of mirroring source structure in tests.

## File Structure

### Docstring

```python
"""test module."""
```

- **Purpose:** Minimal module docstring

### test_main Function

```python
def test_main(main_test_fixture: None) -> None:
    """Test func for main."""
    assert main_test_fixture is None
```

- **Type:** Test function using a fixture
- **Default:** Uses `main_test_fixture` fixture
- **Required:** Yes (for the file to be a valid test)
- **Purpose:** Validates CLI entry point
- **Why pyrig sets it:** Delegates actual testing to the fixture

**How it works:**
1. Pytest discovers `test_main.py`
2. Finds `test_main()` function
3. Sees it requires `main_test_fixture` fixture
4. Runs the fixture (which tests the CLI)
5. Fixture returns `None`
6. Test asserts fixture is `None` (always passes if fixture succeeds)

## The main_test_fixture

The actual testing happens in the `main_test_fixture` fixture:

```python
@pytest.fixture
def main_test_fixture(mocker: MockerFixture) -> None:
    """Fixture for testing main."""
    project_name = PyprojectConfigFile.get_project_name()

    cmds = [
        ["uv", "run", project_name, "--help"],
        ["uv", "run", project_name, "main", "--help"],
    ]

    success = False
    for cmd in cmds:
        completed_process = run_subprocess(cmd, check=False)
        if completed_process.returncode == 0:
            success = True
            break

    assert success, f"Expected main to be callable by one of {cmds}"
```

**What it tests:**
1. **CLI invocation** - `uv run my-awesome-project --help`
2. **Subcommand invocation** - `uv run my-awesome-project main --help`
3. **Exit code** - Ensures command exits with 0 (success)
4. **No crashes** - Command runs without errors

**Why use a fixture:**
- **Reusability** - Other tests can use the same fixture
- **Setup/teardown** - Fixtures can do cleanup
- **Dependency injection** - Pytest manages fixture lifecycle
- **Separation of concerns** - Test logic separate from test function

## Default Configuration

For a project named `my-awesome-project` with package `my_awesome_project`:

**File location:** `tests/test_my_awesome_project/test_main.py`

**File contents:**
```python
"""test module."""


def test_main(main_test_fixture: None) -> None:
    """Test func for main."""
    assert main_test_fixture is None
```

## What Gets Tested

### Command 1: Direct CLI

```bash
uv run my-awesome-project --help
```

**Tests:**
- `pyproject.toml` scripts configuration is correct
- Entry point is properly defined
- CLI responds to `--help`
- No import errors

### Command 2: Subcommand

```bash
uv run my-awesome-project main --help
```

**Tests:**
- Subcommand routing works
- Main function is accessible
- Help text is available

**Why test both:**
- Different CLI frameworks handle these differently
- Ensures flexibility in how users invoke your CLI
- Catches configuration issues

## Running the Test

### Using pytest

```bash
# Run just this test
uv run pytest tests/test_my_awesome_project/test_main.py

# Run with verbose output
uv run pytest tests/test_my_awesome_project/test_main.py -v

# Run with fixture details
uv run pytest tests/test_my_awesome_project/test_main.py --setup-show
```

### Expected Output

```bash
$ uv run pytest tests/test_my_awesome_project/test_main.py -v

tests/test_my_awesome_project/test_main.py::test_main PASSED        [100%]

============================== 1 passed in 0.5s ===============================
```

### If It Fails

```bash
$ uv run pytest tests/test_my_awesome_project/test_main.py -v

tests/test_my_awesome_project/test_main.py::test_main FAILED        [100%]

FAILED tests/test_my_awesome_project/test_main.py::test_main - AssertionError: Expected main to be callable by one of ['uv run my-awesome-project --help', 'uv run my-awesome-project main --help']
```

This indicates a problem with your CLI configuration.

## Customization

You can extend the test to check more CLI behavior:

### Example: Test Multiple Commands

```python
"""test module."""


def test_main(main_test_fixture: None) -> None:
    """Test func for main."""
    assert main_test_fixture is None


def test_version():
    """Test that --version works."""
    from pyrig.src.os.os import run_subprocess
    from pyrig.src.project.mgt import PROJECT_MGT_RUN_ARGS
    from pyrig.dev.configs.pyproject import PyprojectConfigFile

    project_name = PyprojectConfigFile.get_project_name()
    result = run_subprocess(
        [*PROJECT_MGT_RUN_ARGS, project_name, "--version"],
        check=False
    )
    assert result.returncode == 0


def test_subcommands():
    """Test that subcommands are listed."""
    from pyrig.src.os.os import run_subprocess
    from pyrig.src.project.mgt import PROJECT_MGT_RUN_ARGS
    from pyrig.dev.configs.pyproject import PyprojectConfigFile

    project_name = PyprojectConfigFile.get_project_name()
    result = run_subprocess(
        [*PROJECT_MGT_RUN_ARGS, project_name, "--help"],
        check=False,
        capture_output=True
    )
    assert b"main" in result.stdout
```

### Example: Test CLI Output

```python
"""test module."""

import subprocess


def test_main(main_test_fixture: None) -> None:
    """Test func for main."""
    assert main_test_fixture is None


def test_help_output():
    """Test that help output contains expected text."""
    result = subprocess.run(
        ["uv", "run", "my-awesome-project", "--help"],
        capture_output=True,
        text=True
    )

    assert "Usage:" in result.stdout
    assert "Options:" in result.stdout
    assert "--help" in result.stdout
```

## Validation

Pyrig validates that `test_main.py` contains the required function:

```python
@classmethod
def is_correct(cls) -> bool:
    """Check if the test file is valid."""
    return "def test_main" in cls.get_file_content()
```

This allows you to modify the test, but `def test_main` must remain.

## Related Files

- **`{package_name}/main.py`** - The main entry point being tested ([main.md](main.md))
- **`pyproject.toml`** - Defines the CLI entry point ([pyproject.toml](pyproject.md))
- **`tests/conftest.py`** - Provides the `main_test_fixture` ([conftest.md](conftest.md))
- **`tests/test_zero.py`** - Placeholder test ([zero-test.md](zero-test.md))

## Common Issues

### Issue: Test fails with "command not found"

**Symptom:** `uv run my-awesome-project --help` fails

**Cause:** CLI entry point not configured in `pyproject.toml`

**Solution:**
```toml
# pyproject.toml
[project.scripts]
my-awesome-project = "my_awesome_project.cli:main"
```

### Issue: Test fails with import error

**Symptom:** `ModuleNotFoundError: No module named 'my_awesome_project'`

**Cause:** Package not installed

**Solution:**
```bash
# Sync dependencies
uv sync

# Verify package is installed
uv run python -c "import my_awesome_project"
```

### Issue: Test fails with "no such option: --help"

**Symptom:** CLI doesn't recognize `--help`

**Cause:** CLI framework not configured properly

**Solution:**

**For Click:**
```python
# my_awesome_project/cli.py
import click

@click.command()
def main():
    """My awesome CLI."""
    pass
```

**For argparse:**
```python
# my_awesome_project/cli.py
import argparse

def main():
    parser = argparse.ArgumentParser(description="My awesome CLI")
    parser.parse_args()
```

### Issue: Want to test actual CLI functionality

**Symptom:** Test only checks `--help`, not real commands

**Cause:** Default test is minimal

**Solution:**
```python
"""test module."""


def test_main(main_test_fixture: None) -> None:
    """Test func for main."""
    assert main_test_fixture is None


def test_process_command():
    """Test the process command."""
    import subprocess

    result = subprocess.run(
        ["uv", "run", "my-awesome-project", "process", "--input", "test.txt"],
        capture_output=True
    )

    assert result.returncode == 0
    assert b"Processing complete" in result.stdout
```

### Issue: Test is slow

**Symptom:** Test takes several seconds

**Cause:** Spawning subprocess is slow

**Solution:**

**Option 1: Mock the subprocess:**
```python
def test_main(mocker):
    """Test main with mocking."""
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.returncode = 0

    # Your test logic
```

**Option 2: Test the function directly:**
```python
def test_main_function():
    """Test main function directly."""
    from my_awesome_project.cli import main

    # Test the function without subprocess
    result = main()
    assert result is None
```

## Best Practices

### ✅ DO

- **Keep the default test** - It validates CLI configuration
- **Add more tests** - Test actual CLI functionality
- **Test error cases** - Invalid arguments, missing files, etc.
- **Use fixtures** - For setup and teardown
- **Test help text** - Ensure documentation is present

### ❌ DON'T

- **Don't remove test_main** - It's required by pyrig
- **Don't test implementation details** - Test the CLI interface
- **Don't hardcode project name** - Use `PyprojectConfigFile.get_project_name()`
- **Don't skip this test** - It catches real issues
- **Don't make it too complex** - Keep it focused on CLI validation

## Advanced Usage

### Testing CLI with Different Arguments

```python
"""test module."""

import pytest
import subprocess


def test_main(main_test_fixture: None) -> None:
    """Test func for main."""
    assert main_test_fixture is None


@pytest.mark.parametrize("args,expected_exit", [
    (["--help"], 0),
    (["--version"], 0),
    (["invalid-command"], 2),
    (["--invalid-flag"], 2),
])
def test_cli_arguments(args, expected_exit):
    """Test CLI with various arguments."""
    result = subprocess.run(
        ["uv", "run", "my-awesome-project", *args],
        capture_output=True
    )
    assert result.returncode == expected_exit
```

### Testing CLI Output Format

```python
"""test module."""

import json
import subprocess


def test_main(main_test_fixture: None) -> None:
    """Test func for main."""
    assert main_test_fixture is None


def test_json_output():
    """Test that --format json produces valid JSON."""
    result = subprocess.run(
        ["uv", "run", "my-awesome-project", "status", "--format", "json"],
        capture_output=True,
        text=True
    )

    # Should be valid JSON
    data = json.loads(result.stdout)
    assert isinstance(data, dict)
```

### Testing CLI with Environment Variables

```python
"""test module."""

import subprocess
import os


def test_main(main_test_fixture: None) -> None:
    """Test func for main."""
    assert main_test_fixture is None


def test_cli_with_env():
    """Test CLI respects environment variables."""
    env = os.environ.copy()
    env["MY_APP_DEBUG"] = "true"

    result = subprocess.run(
        ["uv", "run", "my-awesome-project", "run"],
        env=env,
        capture_output=True,
        text=True
    )

    assert "DEBUG MODE" in result.stdout
```

## See Also

- [pytest Documentation](https://docs.pytest.org/) - Official pytest docs
- [Click Documentation](https://click.palletsprojects.com/) - Popular CLI framework
- [argparse Documentation](https://docs.python.org/3/library/argparse.html) - Standard library CLI
- [Typer Documentation](https://typer.tiangolo.com/) - Modern CLI framework
- [main.py](main.md) - Main entry point file
- [conftest.py](conftest.md) - Pytest configuration
- [pyproject.toml](pyproject.md) - CLI entry point configuration
- [Getting Started Guide](../getting-started.md) - Initial project setup


