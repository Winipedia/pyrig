# CLI: Command-Line Interface

This document describes pyrig's command-line interface (CLI) system, which provides commands for project initialization, test generation, artifact building, and more. The CLI is auto-generated from Python functions using Typer.

## Overview

pyrig provides a CLI that is:
- **Auto-generated**: Functions in `subcommands.py` automatically become CLI commands
- **Extensible**: Dependent packages can add their own commands
- **Convention-based**: Function names become command names (snake_case → kebab-case)
- **Self-documenting**: Function docstrings become CLI help text

## Quick Reference

| Command | Description |
|---------|-------------|
| `pyrig init` | Full project initialization (configs, structure, tests, hooks) |
| `pyrig mkroot` | Create project structure and config files |
| `pyrig mktests` | Generate test skeletons for untested code |
| `pyrig mkinits` | Create missing `__init__.py` files |
| `pyrig build` | Build all artifacts via Builder subclasses |
| `pyrig protect-repo` | Set up GitHub branch protection and security |
| `pyrig main` | Run the project's main entry point |

## Installation and Activation

The CLI is defined as a console script entry point in `pyproject.toml`:

```toml
[project.scripts]
pyrig = "pyrig.dev.cli.cli:main"
```

After installation (`uv sync`), the CLI becomes available:

```bash
# Run via uv
uv run pyrig --help

# After activation, directly
pyrig --help
```

## Available Commands

### `pyrig init`

Full project initialization. This is the main command for setting up a new pyrig project or updating an existing one.

```bash
uv run pyrig init
```

**What it does (in order):**
1. Writes priority config files (pyproject.toml with dev dependencies)
2. Installs dependencies with `uv sync`
3. Updates dependencies to latest versions
4. Creates project structure via `mkroot`
5. Generates test skeletons via `mktests`
6. Runs pre-commit hooks for initial formatting
7. Runs tests to verify setup
8. Re-installs to activate CLI entry points
9. Commits all changes with "pyrig: Initial commit"

**When to use:**
- Initial project setup after cloning
- After adding pyrig as a dependency
- To reset/update all configurations to pyrig defaults

---

### `pyrig mkroot`

Creates the project structure and all configuration files.

```bash
uv run pyrig mkroot
```

**What it does:**
- Initializes all ConfigFile subclasses
- Creates `__init__.py` files for source and test packages
- Does not overwrite existing files (safe to re-run)

**When to use:**
- After adding new ConfigFile classes
- To regenerate missing config files
- As part of CI/CD to verify config consistency

---

### `pyrig mktests`

Generates test skeletons for all untested functions and classes.

```bash
uv run pyrig mktests
```

**What it does:**
- Walks all modules in the source package
- Creates test modules mirroring source structure
- Generates skeleton tests with `raise NotImplementedError`
- Does not overwrite existing tests

**When to use:**
- After adding new source files
- To quickly scaffold tests for new code
- As part of development workflow

---

### `pyrig mkinits`

Creates missing `__init__.py` files for all packages.

```bash
uv run pyrig mkinits
```

**What it does:**
- Finds all namespace packages (directories without `__init__.py`)
- Creates empty `__init__.py` files for them
- Does not overwrite existing files

**When to use:**
- After adding new directories/packages
- To fix namespace package issues
- When imports fail due to missing `__init__.py`

---

### `pyrig build`

Builds all project artifacts.

```bash
uv run pyrig build
```

**What it does:**
- Discovers all Builder subclasses
- Invokes each Builder to create its artifacts
- Supports artifact generation from templates, APIs, etc.

**When to use:**
- After modifying artifact templates
- Before committing generated files
- As part of CI/CD to verify artifacts are up-to-date

---

### `pyrig protect-repo`

Configures GitHub repository security settings and branch protection.

```bash
uv run pyrig protect-repo
```

**What it does:**
- Sets secure repository settings (delete branches on merge, etc.)
- Creates/updates branch protection rulesets
- Requires GitHub token with appropriate permissions

**Protection rules enforced:**
- Required pull request reviews with code owner approval
- Required status checks (health check workflow must pass)
- Linear commit history (no merge commits)
- Signed commits
- No force pushes or deletions

---

### `pyrig main`

Runs the project's main entry point.

```bash
uv run pyrig main
```

**What it does:**
- Calls the `main()` function from `{package}/main.py`
- By default, raises `NotImplementedError` with instructions

**How to customize:**
Edit `your_project/main.py`:

```python
def main() -> None:
    """Main entrypoint for the project."""
    print("Hello from my project!")
```

---

## How the CLI Works

### Architecture

The CLI is built using [Typer](https://typer.tiangolo.com/), with automatic command discovery:

```
pyrig/dev/cli/
├── cli.py          # Entry point and command registration
└── subcommands.py  # Function definitions → CLI commands
```

### Entry Point: `cli.py`

The main entry point discovers and registers commands:

```python
app = typer.Typer()

def add_subcommands() -> None:
    # 1. Get project name from CLI invocation
    project_name = Path(sys.argv[0]).name
    pkg_name = PyprojectConfigFile.get_pkg_name_from_project_name(project_name)

    # 2. Register main.py's main() as the "main" command
    main_module = import_module_from_path(f"{pkg_name}.main")
    app.command()(main_module.main)

    # 3. Register all functions from subcommands.py
    subcommands_module = import_module_from_path(f"{pkg_name}.dev.cli.subcommands")
    for sub_cmd in get_all_functions_from_module(subcommands_module):
        app.command()(sub_cmd)

def main() -> None:
    add_subcommands()
    app()
```

### Command Discovery

All functions in `subcommands.py` automatically become CLI commands:

```python
# pyrig/dev/cli/subcommands.py

def mkroot() -> None:
    """Creates the root of the project."""
    make_project_root()

def mktests() -> None:
    """Create all test files for the project."""
    make_test_skeletons()

def mkinits() -> None:
    """Create all __init__.py files for the project."""
    make_init_files()
```

Becomes:
```
$ pyrig --help
Commands:
  mkroot   Creates the root of the project.
  mktests  Create all test files for the project.
  mkinits  Create all __init__.py files for the project.
  ...
```

### Naming Convention

| Python Function | CLI Command |
|----------------|-------------|
| `mkroot()` | `mkroot` |
| `mktests()` | `mktests` |
| `mkinits()` | `mkinits` |
| `protect_repo()` | `protect-repo` |
| `init()` | `init` |

The conversion is handled automatically by Typer (snake_case → kebab-case).

### Docstrings → Help Text

Function docstrings become CLI command descriptions:

```python
def init() -> None:
    """Set up the project.

    This is the setup command when you created the project from scratch.
    It will init all config files, create the root, create tests, and run
    all pre-commit hooks and tests.
    """
    init_cmd()
```

```bash
$ pyrig init --help
Usage: pyrig init [OPTIONS]

  Set up the project.

  This is the setup command when you created the project from scratch.
  It will init all config files, create the root, create tests, and run
  all pre-commit hooks and tests.
```

---

## Your Project's CLI

When your project depends on pyrig, it gets its own separate CLI. Your project's CLI includes:
- The `main` command (from your `main.py`)
- Any custom commands you define in your `subcommands.py`

**Important:** pyrig's commands (`init`, `mkroot`, `mktests`, `mkinits`, etc.) are only available via `pyrig`, not via your project's CLI. You always use `uv run pyrig <command>` for pyrig operations.

### How It Works

1. The CLI discovers the project name from `sys.argv[0]` (e.g., `your-project`)
2. It imports `{your_project}.main` and `{your_project}.dev.cli.subcommands`
3. All functions defined in your subcommands become commands

### Adding Custom Commands

Create `your_project/dev/cli/subcommands.py`:

```python
"""Custom CLI subcommands for your project."""

from your_project.src.deployment import deploy as deploy_cmd

def deploy() -> None:
    """Deploy the application to production.

    This runs the deployment pipeline with all safety checks.
    """
    deploy_cmd()

def migrate_db() -> None:
    """Run database migrations."""
    from your_project.src.database import run_migrations
    run_migrations()
```

After running `uv sync`, your project has its own CLI:

```bash
$ your-project --help
Commands:
  main          Main entrypoint for the project.
  deploy        Deploy the application to production.
  migrate-db    Run database migrations.
```

For pyrig operations, you still use pyrig directly:

```bash
$ uv run pyrig --help
Commands:
  init          Set up the project.
  mkroot        Creates the root of the project.
  mktests       Create all test files for the project.
  mkinits       Create all __init__.py files for the project.
  build         Build all artifacts.
  protect-repo  Protect the repository.
  main          Main entrypoint for the project.
```

### Best Practices for Custom Commands

1. **Keep subcommands.py thin** — Define logic elsewhere, call it from wrapper functions
2. **Write clear docstrings** — They become the CLI help text
3. **Use type hints** — Typer uses them for argument parsing
4. **Follow naming conventions** — snake_case for functions, they become kebab-case

---

## Commands with Arguments

Typer automatically converts function parameters to CLI arguments and options.

### Example: Custom Command with Arguments

```python
# your_project/dev/cli/subcommands.py

def greet(name: str, count: int = 1, loud: bool = False) -> None:
    """Greet someone.

    Args:
        name: The name to greet
        count: Number of times to greet
        loud: Whether to shout the greeting
    """
    greeting = f"Hello, {name}!"
    if loud:
        greeting = greeting.upper()
    for _ in range(count):
        print(greeting)
```

Usage:

```bash
$ your-project greet Alice
Hello, Alice!

$ your-project greet Bob --count 3 --loud
HELLO, BOB!
HELLO, BOB!
HELLO, BOB!

$ your-project greet --help
Usage: your-project greet [OPTIONS] NAME

  Greet someone.

Arguments:
  NAME  The name to greet  [required]

Options:
  --count INTEGER  Number of times to greet  [default: 1]
  --loud           Whether to shout the greeting
  --help           Show this message and exit.
```

### Type Hints and CLI Arguments

| Python Type | CLI Behavior |
|-------------|--------------|
| `str` | Required argument |
| `int` | Parsed as integer |
| `bool` | Flag (`--flag` / `--no-flag`) |
| `Optional[str]` | Optional argument |
| `str = "default"` | Optional with default |
| `list[str]` | Multiple values allowed |

---

## Common Workflows

### Initial Project Setup

```bash
# Clone or create your project
git clone https://github.com/your/project.git
cd project

# Run full initialization
uv run pyrig init
```

### Daily Development

```bash
# After adding new source files
uv run pyrig mktests

# Before committing
uv run pytest
```

### After Modifying Configurations

```bash
# Regenerate all config files
uv run pyrig mkroot
```

### After Adding Custom Builders

```bash
# Regenerate all artifacts
uv run pyrig build
```

### Setting Up GitHub Repository

```bash
# After pushing to GitHub
export GITHUB_TOKEN=your_token
uv run pyrig protect-repo
```

---

## Running Commands Programmatically

pyrig provides utilities for invoking CLI commands from code:

```python
from pyrig.src.project.mgt import (
    get_project_mgt_run_cli_cmd_args,
    get_project_mgt_run_pyrig_cli_cmd_args,
)
from pyrig.dev.cli.subcommands import mktests
from pyrig.src.os.os import run_subprocess

# Build args for pyrig CLI command
args = get_project_mgt_run_pyrig_cli_cmd_args(mktests)
# Returns: ['uv', 'run', 'pyrig', 'mktests']

# Build args for your project's CLI command
args = get_project_mgt_run_cli_cmd_args(mktests)
# Returns: ['uv', 'run', 'your-project', 'mktests']

# Execute the command
run_subprocess(args)
```

---

## CLI File Structure

For a complete pyrig project, the CLI files are organized as:

```
your_project/
├── main.py                    # main() → "your-project main"
└── dev/
    └── cli/
        ├── __init__.py
        ├── cli.py             # Entry point (copied from pyrig)
        └── subcommands.py     # Your custom commands + pyrig commands
```

The `cli.py` file is auto-generated from pyrig and should not be modified. Add custom commands to `subcommands.py`.

---

## Troubleshooting

### "Command not found"

**Cause:** The CLI hasn't been installed or activated.

**Solution:**
```bash
uv sync
uv run your-project --help
```

### "ModuleNotFoundError" when running commands

**Cause:** Dependencies not installed or virtual environment not activated.

**Solution:**
```bash
uv sync
uv run pyrig init  # Always use 'uv run' prefix
```

### Custom command not appearing

**Cause:** Function is imported, not defined in subcommands.py.

**Solution:** Only functions defined directly in subcommands.py become commands. The CLI filters out imported functions:

```python
# This WON'T become a command (imported)
from somewhere import my_function

# This WILL become a command (defined here)
def my_command() -> None:
    """My command."""
    my_function()
```

### Command name different than expected

**Cause:** Typer converts snake_case to kebab-case.

**Reference:**
```
protect_repo()  → protect-repo
do_something()  → do-something
```

---

## Summary

pyrig's CLI system provides:

1. **Automatic command generation** from functions in `subcommands.py`
2. **Self-documenting help** from function docstrings
3. **Separate CLIs** — pyrig commands via `pyrig`, your commands via `your-project`
4. **Typer-powered** argument parsing with type hints
5. **Convention-based** naming (snake_case → kebab-case)

Your project gets its own CLI for project-specific commands, while pyrig operations are always run via `uv run pyrig`.
