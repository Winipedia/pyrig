# SubcommandsConfigFile

## Overview

**File Location:** `{package_name}/dev/cli/subcommands.py`
**ConfigFile Class:** `SubcommandsConfigFile`
**File Type:** Python
**Priority:** Standard

Creates a file where you can define custom CLI subcommands for your project. All functions in this file are automatically discovered and added to your CLI.

## Purpose

The `{package_name}/dev/cli/subcommands.py` file provides CLI extensibility:

- **Custom Commands** - Define project-specific CLI commands
- **Automatic Discovery** - Functions are automatically registered
- **Typer Integration** - Uses Typer for CLI framework
- **Best Practices** - Encourages separation of logic and CLI
- **Documentation** - Docstrings become command help text

## Subcommands vs Shared Subcommands

**Key Difference:**

| Feature | `subcommands.py` | `shared_subcommands.py` |
|---------|------------------|-------------------------|
| **Scope** | Project-specific only | Available in all dependent packages |
| **Use Case** | Commands unique to this project | Commands shared across package ecosystem |
| **Discovery** | Only in this package | Across all packages depending on pyrig |
| **Example** | `migrate`, `seed-db`, `run-worker` | `version`, `deploy`, `security-scan` |

**Use `subcommands.py` when:**
- Command is specific to THIS project only
- Command uses project-specific logic
- You don't want other packages to inherit this command

**Use `shared_subcommands.py` when:**
- Building a base package with common commands
- Creating organization-wide tooling
- Commands should be available in ALL packages that depend on yours

**Example:**

```python
# my_app/dev/cli/subcommands.py (project-specific)
def migrate() -> None:
    """Run database migrations for my_app."""
    # Only available in my_app
    pass

# company_base/dev/cli/shared_subcommands.py (cross-package)
def deploy() -> None:
    """Deploy any application."""
    # Available in ALL packages that depend on company_base
    pass
```

See [shared_subcommands.py](shared-subcommands.md) for cross-package commands and [Multi-Package Architecture](../multi-package-architecture.md) for more details.

### Why pyrig manages this file

pyrig creates `dev/cli/subcommands.py` to:
1. **Immediate extensibility** - You can add commands from day one
2. **Automatic registration** - No manual command registration needed
3. **Best practices** - Encourages clean CLI design
4. **Documentation** - Docstring explains the pattern
5. **Consistency** - All pyrig projects have the same CLI structure

The file is created during `pyrig init` with only the docstring from pyrig's `dev.cli.subcommands` module.

## File Location

The file is placed in your package's `dev/cli` directory:

```
my-awesome-project/
├── my_awesome_project/
│   ├── __init__.py
│   └── dev/
│       ├── __init__.py
│       └── cli/
│           ├── __init__.py
│           └── subcommands.py  # <-- Here
└── pyproject.toml
```

This mirrors pyrig's structure:

```
pyrig/
├── pyrig/
│   ├── __init__.py
│   └── dev/
│       ├── __init__.py
│       └── cli/
│           ├── __init__.py
│           └── subcommands.py  # <-- Mirrored from here
└── pyproject.toml
```

## File Structure

### Docstring Only

The file contains **only the docstring** from pyrig's `dev.cli.subcommands`:

```python
"""Subcommands for the CLI.

They will be automatically imported and added to the CLI
IMPORTANT: All funcs in this file will be added as subcommands.
So best to define the logic elsewhere and just call it here in a wrapper.
"""
```

- **Type:** Module docstring
- **Default:** Copied from `pyrig.dev.cli.subcommands`
- **Required:** Yes (minimal module marker)
- **Purpose:** Documents the module and explains the pattern
- **Why pyrig sets it:** Provides guidance on how to use the file

**Why only the docstring:**
- **Minimal** - Doesn't impose commands
- **Flexible** - You can add your own commands
- **Documentation** - Preserves pyrig's guidance
- **Module marker** - Valid Python module

**Important Note:**
The docstring emphasizes: **All functions in this file will be added as subcommands.**
This means you should keep business logic elsewhere and use this file only for CLI wrappers.

## Default Configuration

For a project named `my-awesome-project` with package `my_awesome_project`:

**File location:** `my_awesome_project/dev/cli/subcommands.py`

**File contents:**
```python
"""Subcommands for the CLI.

They will be automatically imported and added to the CLI
IMPORTANT: All funcs in this file will be added as subcommands.
So best to define the logic elsewhere and just call it here in a wrapper.
"""
```

## How It Works

### Automatic Discovery

When you run your CLI, pyrig:

1. **Imports subcommands.py** - Loads your subcommands module
2. **Discovers functions** - Finds all public functions
3. **Registers commands** - Adds them to the Typer app
4. **Makes them available** - Commands are now callable

### Example Flow

```python
# my_awesome_project/dev/cli/subcommands.py
def deploy() -> None:
    """Deploy the application."""
    print("Deploying...")
```

```bash
# Automatically available as:
$ uv run my-awesome-project deploy
Deploying...

# Help text from docstring:
$ uv run my-awesome-project deploy --help
Usage: my-awesome-project deploy [OPTIONS]

  Deploy the application.

Options:
  --help  Show this message and exit.
```

## Creating Custom Subcommands

### Example: Simple Command

```python
# my_awesome_project/dev/cli/subcommands.py
"""Subcommands for the CLI.

They will be automatically imported and added to the CLI
IMPORTANT: All funcs in this file will be added as subcommands.
So best to define the logic elsewhere and just call it here in a wrapper.
"""


def hello() -> None:
    """Say hello."""
    print("Hello from my-awesome-project!")
```

```bash
$ uv run my-awesome-project hello
Hello from my-awesome-project!
```

### Example: Command with Arguments

```python
# my_awesome_project/dev/cli/subcommands.py
"""Subcommands for the CLI.

They will be automatically imported and added to the CLI
IMPORTANT: All funcs in this file will be added as subcommands.
So best to define the logic elsewhere and just call it here in a wrapper.
"""


def greet(name: str) -> None:
    """Greet someone by name.

    Args:
        name: The name to greet
    """
    print(f"Hello, {name}!")
```

```bash
$ uv run my-awesome-project greet Alice
Hello, Alice!

$ uv run my-awesome-project greet --help
Usage: my-awesome-project greet [OPTIONS] NAME

  Greet someone by name.

Arguments:
  NAME  The name to greet  [required]

Options:
  --help  Show this message and exit.
```

### Example: Command with Options

```python
# my_awesome_project/dev/cli/subcommands.py
"""Subcommands for the CLI.

They will be automatically imported and added to the CLI
IMPORTANT: All funcs in this file will be added as subcommands.
So best to define the logic elsewhere and just call it here in a wrapper.
"""

import typer


def deploy(
    environment: str = typer.Option("production", help="Deployment environment"),
    dry_run: bool = typer.Option(False, help="Perform a dry run"),
) -> None:
    """Deploy the application.

    Args:
        environment: The environment to deploy to
        dry_run: Whether to perform a dry run
    """
    if dry_run:
        print(f"[DRY RUN] Would deploy to {environment}")
    else:
        print(f"Deploying to {environment}...")
```

```bash
$ uv run my-awesome-project deploy
Deploying to production...

$ uv run my-awesome-project deploy --environment staging
Deploying to staging...

$ uv run my-awesome-project deploy --dry-run
[DRY RUN] Would deploy to production
```

## Best Practice: Separate Logic from CLI

**The docstring emphasizes:** Define logic elsewhere and use subcommands.py only for wrappers.

### ❌ Bad: Logic in subcommands.py

```python
# my_awesome_project/dev/cli/subcommands.py
"""Subcommands for the CLI."""


def deploy() -> None:
    """Deploy the application."""
    # DON'T: Put all logic here
    import subprocess
    import sys

    # Build the application
    result = subprocess.run(["uv", "build"], check=False)
    if result.returncode != 0:
        sys.exit(1)

    # Upload to server
    result = subprocess.run(["scp", "dist/*", "server:/app/"], check=False)
    if result.returncode != 0:
        sys.exit(1)

    # Restart service
    result = subprocess.run(["ssh", "server", "systemctl restart app"], check=False)
    if result.returncode != 0:
        sys.exit(1)

    print("Deployment complete!")
```

### ✅ Good: Logic in separate module

```python
# my_awesome_project/deployment.py
"""Deployment logic."""

import subprocess
import sys


def deploy_application(environment: str = "production") -> None:
    """Deploy the application to the specified environment.

    Args:
        environment: The environment to deploy to
    """
    # Build the application
    result = subprocess.run(["uv", "build"], check=False)
    if result.returncode != 0:
        sys.exit(1)

    # Upload to server
    server = f"{environment}.example.com"
    result = subprocess.run(["scp", "dist/*", f"{server}:/app/"], check=False)
    if result.returncode != 0:
        sys.exit(1)

    # Restart service
    result = subprocess.run(["ssh", server, "systemctl restart app"], check=False)
    if result.returncode != 0:
        sys.exit(1)

    print(f"Deployment to {environment} complete!")
```

```python
# my_awesome_project/dev/cli/subcommands.py
"""Subcommands for the CLI.

They will be automatically imported and added to the CLI
IMPORTANT: All funcs in this file will be added as subcommands.
So best to define the logic elsewhere and just call it here in a wrapper.
"""

import typer


def deploy(
    environment: str = typer.Option("production", help="Deployment environment"),
) -> None:
    """Deploy the application.

    Args:
        environment: The environment to deploy to
    """
    from my_awesome_project.deployment import deploy_application

    deploy_application(environment)
```

**Benefits:**
- **Testable** - Logic can be tested without CLI
- **Reusable** - Logic can be used programmatically
- **Maintainable** - Separation of concerns
- **Clean** - subcommands.py stays minimal

## Pyrig's Built-in Subcommands

Pyrig provides several built-in subcommands:

### mkroot

```python
def mkroot() -> None:
    """Creates the root of the project.

    This inits all ConfigFiles and creates __init__.py files for the src
    and tests package where they are missing. It does not overwrite any
    existing files.
    """
    from pyrig.dev.cli.commands.create_root import make_project_root

    make_project_root()
```

```bash
$ uv run pyrig mkroot
```

### init

```python
def init() -> None:
    """Initialize the project.

    Sets up the complete project structure including configuration files,
    directory structure, and dependencies.
    """
    from pyrig.dev.cli.commands.setup import setup_project

    setup_project()
```

```bash
$ uv run pyrig init
```

### build

```python
def build() -> None:
    """Build the project.

    Runs all Builder subclasses to generate code, documentation, and
    other artifacts.
    """
    from pyrig.dev.cli.commands.build import build_project

    build_project()
```

```bash
$ uv run pyrig build
```

### mktests

```python
def mktests() -> None:
    """Create test skeletons.

    Generates test files for all modules that don't have tests yet.
    """
    from pyrig.dev.cli.commands.create_tests import make_test_skeletons

    make_test_skeletons()
```

```bash
$ uv run pyrig mktests
```

### mkinits

```python
def mkinits() -> None:
    """Create __init__.py files.

    Generates __init__.py files for all packages that don't have them.
    """
    from pyrig.dev.cli.commands.create_inits import make_init_files

    make_init_files()
```

```bash
$ uv run pyrig mkinits
```

## Advanced Examples

### Command with Multiple Arguments

```python
# my_awesome_project/dev/cli/subcommands.py
"""Subcommands for the CLI."""

import typer


def create_user(
    username: str,
    email: str,
    admin: bool = typer.Option(False, help="Make user an admin"),
    active: bool = typer.Option(True, help="Activate user immediately"),
) -> None:
    """Create a new user.

    Args:
        username: The username
        email: The user's email address
        admin: Whether to make the user an admin
        active: Whether to activate the user immediately
    """
    from my_awesome_project.users import create_user as _create_user

    _create_user(username, email, admin=admin, active=active)
```

### Command with File Input

```python
# my_awesome_project/dev/cli/subcommands.py
"""Subcommands for the CLI."""

from pathlib import Path
import typer


def process_file(
    input_file: Path = typer.Argument(..., help="Input file to process"),
    output_file: Path = typer.Option(None, help="Output file (default: stdout)"),
) -> None:
    """Process a file.

    Args:
        input_file: The input file to process
        output_file: The output file (optional)
    """
    from my_awesome_project.processing import process_file as _process_file

    _process_file(input_file, output_file)
```

### Command with Confirmation

```python
# my_awesome_project/dev/cli/subcommands.py
"""Subcommands for the CLI."""

import typer


def delete_all(
    force: bool = typer.Option(False, "--force", help="Skip confirmation"),
) -> None:
    """Delete all data.

    Args:
        force: Skip confirmation prompt
    """
    if not force:
        confirmed = typer.confirm("Are you sure you want to delete all data?")
        if not confirmed:
            typer.echo("Cancelled.")
            raise typer.Abort()

    from my_awesome_project.database import delete_all_data

    delete_all_data()
    typer.echo("All data deleted.")
```

## Related Files

- **`{package_name}/dev/cli/__init__.py`** - CLI package init (created by pyrig)
- **`{package_name}/dev/cli/cli.py`** - CLI entry point (if customized)
- **`{package_name}/main.py`** - Main entry point ([main.md](main.md))
- **`pyproject.toml`** - CLI entry point configuration ([pyproject.md](pyproject.md))

## Common Issues

### Issue: Command not found

**Symptom:** `Error: No such command 'mycommand'`

**Cause:** Function not in subcommands.py or not public

**Solution:**
```python
# Ensure function is in subcommands.py
# Ensure function doesn't start with underscore

# Good:
def mycommand() -> None:
    """My command."""
    pass

# Bad (private function, won't be registered):
def _mycommand() -> None:
    """My command."""
    pass
```

### Issue: Command has wrong name

**Symptom:** Command name doesn't match function name

**Cause:** Typer converts underscores to hyphens

**Solution:**
```python
# Function name: deploy_app
def deploy_app() -> None:
    """Deploy the app."""
    pass

# CLI command: deploy-app (underscores become hyphens)
$ uv run my-awesome-project deploy-app
```

### Issue: Arguments not working

**Symptom:** Arguments not recognized

**Cause:** Missing type hints

**Solution:**
```python
# Bad: No type hints
def greet(name):
    """Greet someone."""
    print(f"Hello, {name}!")

# Good: With type hints
def greet(name: str) -> None:
    """Greet someone."""
    print(f"Hello, {name}!")
```

### Issue: Want optional arguments

**Symptom:** How to make arguments optional?

**Cause:** Need to use typer.Option

**Solution:**
```python
import typer

def deploy(
    environment: str = typer.Option("production", help="Environment"),
) -> None:
    """Deploy the application."""
    pass
```

## Best Practices

### ✅ DO

- **Keep it minimal** - Only CLI wrappers here
- **Use type hints** - Required for Typer
- **Add docstrings** - They become help text
- **Separate logic** - Put business logic elsewhere
- **Use typer.Option** - For optional arguments

### ❌ DON'T

- **Don't put logic here** - Use separate modules
- **Don't use private functions** - They won't be registered
- **Don't skip type hints** - Typer needs them
- **Don't skip docstrings** - They're the help text
- **Don't make it complex** - Keep commands simple

## See Also

- [Typer Documentation](https://typer.tiangolo.com/) - CLI framework
- [Click Documentation](https://click.palletsprojects.com/) - Underlying framework
- [main.py](main.md) - Main entry point
- [pyproject.toml](pyproject.md) - CLI configuration
- [Getting Started Guide](../getting-started.md) - Initial project setup


