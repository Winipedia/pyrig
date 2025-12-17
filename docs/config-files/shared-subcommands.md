# SharedSubcommandsConfigFile

## Overview

**File Location:** `{package_name}/dev/cli/shared_subcommands.py`
**ConfigFile Class:** `SharedSubcommandsConfigFile`
**File Type:** Python
**Priority:** Standard

Creates a file where you can define custom CLI subcommands that are **automatically available in all packages that depend on your package**. This is a key feature of pyrig's multi-package architecture.

## Purpose

The `{package_name}/dev/cli/shared_subcommands.py` file provides cross-package CLI extensibility:

- **Cross-Package Commands** - Commands available in all dependent packages
- **Automatic Discovery** - Functions are automatically registered across packages
- **Multi-Package Architecture** - Build package ecosystems with shared tooling
- **Typer Integration** - Uses Typer for CLI framework
- **Organization-Wide Tooling** - Create common commands for all your projects

### Why pyrig manages this file

pyrig creates `dev/cli/shared_subcommands.py` to:
1. **Enable multi-package CLI** - Share commands across your package ecosystem
2. **Automatic registration** - No manual command registration needed
3. **Built-in example** - The `version` command is a shared subcommand
4. **Documentation** - Docstring explains the pattern
5. **Consistency** - All pyrig projects can share CLI commands

The file is created during `pyrig init` with only the docstring from pyrig's `dev.cli.shared_subcommands` module.

## Shared Subcommands vs Regular Subcommands

**Key Difference:**

| Feature | `subcommands.py` | `shared_subcommands.py` |
|---------|------------------|-------------------------|
| **Scope** | Project-specific only | Available in all dependent packages |
| **Use Case** | Commands unique to this project | Commands shared across package ecosystem |
| **Discovery** | Only in this package | Across all packages depending on pyrig |
| **Example** | `deploy`, `migrate`, `seed-db` | `version`, `lint-all`, `security-scan` |

**Use `shared_subcommands.py` when:**
- Building a base package with common commands
- Creating organization-wide tooling
- Commands should be available in ALL packages that depend on yours

**Use `subcommands.py` when:**
- Command is specific to THIS project only
- Command uses project-specific logic
- You don't want other packages to inherit this command

See [subcommands.py](subcommands.md) for project-specific commands.

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
│           ├── subcommands.py         # Project-specific commands
│           └── shared_subcommands.py  # <-- Cross-package commands
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
│           ├── subcommands.py
│           └── shared_subcommands.py  # <-- Mirrored from here
└── pyproject.toml
```

## File Structure

### Docstring Only

The file contains **only the docstring** from pyrig's `dev.cli.shared_subcommands`:

```python
"""Shared commands for the CLI.

This module provides shared CLI commands that can be used by multiple
packages in a multi-package architecture. These commands are automatically
discovered and added to the CLI by pyrig.
Example is version command that is available in all packages.
uv run my-awesome-project version will return my-awesome-project version 0.1.0
"""
```

- **Type:** Module docstring
- **Default:** Copied from `pyrig.dev.cli.shared_subcommands`
- **Required:** Yes (minimal module marker)
- **Purpose:** Documents the module and explains the pattern
- **Why pyrig sets it:** Provides guidance on cross-package commands

**Why only the docstring:**
- **Minimal** - Doesn't impose commands
- **Flexible** - You can add your own shared commands
- **Documentation** - Preserves pyrig's guidance
- **Module marker** - Valid Python module

## Default Configuration

For a project named `my-awesome-project` with package `my_awesome_project`:

**File location:** `my_awesome_project/dev/cli/shared_subcommands.py`

**File contents:**
```python
"""Shared commands for the CLI.

This module provides shared CLI commands that can be used by multiple
packages in a multi-package architecture. These commands are automatically
discovered and added to the CLI by pyrig.
Example is version command that is available in all packages.
uv run my-awesome-project version will return my-awesome-project version 0.1.0
"""
```

## Built-In Example: The `version` Command

Pyrig includes a built-in shared subcommand as an example:

```python
# pyrig/dev/cli/shared_subcommands.py
from importlib.metadata import version as get_version
import typer
from pyrig.dev.utils.cli import get_project_name_from_argv

def version() -> None:
    """Display the version information."""
    project_name = get_project_name_from_argv()
    typer.echo(f"{project_name} version {get_version(project_name)}")
```

This command is automatically available in **every package that depends on pyrig**:

```bash
# In pyrig itself
$ uv run pyrig version
pyrig version 0.1.0

# In your project
$ uv run my-awesome-project version
my-awesome-project version 1.2.3

# In any dependent package
$ uv run other-service version
other-service version 2.0.0
```

## How It Works

### Automatic Cross-Package Discovery

When you run your CLI, pyrig:

1. **Builds dependency graph** - Finds all packages depending on pyrig
2. **Discovers shared_subcommands modules** - Looks for `<package>.dev.cli.shared_subcommands`
3. **Imports all functions** - Finds all public functions in each module
4. **Registers commands** - Adds them to the Typer app
5. **Makes them available** - Commands are now callable in ALL dependent packages

### Example Flow

```
Package Ecosystem:
  pyrig (has version command in shared_subcommands.py)
    ↑
    └── company-base (has deploy, lint-all commands in shared_subcommands.py)
          ↑
          └── my-app (has no shared_subcommands, but gets all parent commands)
```

When you run `uv run my-app --help`, you see:
- `version` (from pyrig)
- `deploy` (from company-base)
- `lint-all` (from company-base)
- Plus all commands from `my-app/dev/cli/subcommands.py`

## Creating Custom Shared Subcommands

### Example: Organization-Wide Deploy Command

Create a base package for your organization:

```python
# company_base/dev/cli/shared_subcommands.py
"""Shared commands for the CLI.

This module provides shared CLI commands that can be used by multiple
packages in a multi-package architecture. These commands are automatically
discovered and added to the CLI by pyrig.
Example is version command that is available in all packages.
uv run my-awesome-project version will return my-awesome-project version 0.1.0
"""

import typer


def deploy() -> None:
    """Deploy the application to production."""
    project_name = _get_project_name()
    typer.echo(f"Deploying {project_name} to production...")
    # Your deployment logic here


def _get_project_name() -> str:
    """Get the current project name."""
    from pyrig.dev.utils.cli import get_project_name_from_argv
    return get_project_name_from_argv()
```

Now **every package** that depends on `company-base` gets the `deploy` command:

```bash
# In service-a
$ uv run service-a deploy
Deploying service-a to production...

# In service-b
$ uv run service-b deploy
Deploying service-b to production...

# In any other service
$ uv run my-api deploy
Deploying my-api to production...
```

### Example: Security Scanning Command

```python
# company_base/dev/cli/shared_subcommands.py
"""Shared commands for the CLI."""

import typer
from pathlib import Path


def security_scan() -> None:
    """Run security scanning on the project."""
    typer.echo("Running security scan...")

    # Run bandit
    from pyrig.src.os.os import run_subprocess
    result = run_subprocess(["bandit", "-r", "."])

    if result.returncode == 0:
        typer.echo("✅ Security scan passed!")
    else:
        typer.echo("❌ Security issues found!")
        raise typer.Exit(1)


def lint_all() -> None:
    """Run all linting tools."""
    typer.echo("Running ruff...")
    from pyrig.src.os.os import run_subprocess

    run_subprocess(["ruff", "check", "."])
    run_subprocess(["ruff", "format", "--check", "."])

    typer.echo("✅ Linting complete!")
```

Available in all dependent packages:

```bash
$ uv run my-app security-scan
Running security scan...
✅ Security scan passed!

$ uv run my-app lint-all
Running ruff...
✅ Linting complete!
```

### Example: Database Management Commands

```python
# data_tools/dev/cli/shared_subcommands.py
"""Shared database commands."""

import typer


def db_migrate() -> None:
    """Run database migrations."""
    typer.echo("Running database migrations...")
    # Your migration logic here


def db_seed() -> None:
    """Seed the database with test data."""
    typer.echo("Seeding database...")
    # Your seeding logic here


def db_reset() -> None:
    """Reset the database (WARNING: destructive)."""
    if typer.confirm("Are you sure you want to reset the database?"):
        typer.echo("Resetting database...")
        # Your reset logic here
    else:
        typer.echo("Cancelled.")
```

## Best Practice: Separate Logic from CLI

**The docstring emphasizes:** Define logic elsewhere and use shared_subcommands.py only for wrappers.

### ❌ DON'T: Put business logic in shared_subcommands.py

```python
# company_base/dev/cli/shared_subcommands.py
def deploy() -> None:
    """Deploy the application."""
    # DON'T: 100 lines of deployment logic here
    import boto3
    client = boto3.client('ecs')
    # ... lots of AWS logic ...
```

### ✅ DO: Keep logic in src/, use shared_subcommands.py as wrapper

```python
# company_base/src/deployment/deployer.py
"""Deployment logic."""

class Deployer:
    """Handles application deployment."""

    def deploy(self, project_name: str) -> None:
        """Deploy the application."""
        # All your deployment logic here
        pass


# company_base/dev/cli/shared_subcommands.py
"""Shared commands for the CLI."""

import typer


def deploy() -> None:
    """Deploy the application to production."""
    from company_base.src.deployment.deployer import Deployer
    from pyrig.dev.utils.cli import get_project_name_from_argv

    project_name = get_project_name_from_argv()
    deployer = Deployer()
    deployer.deploy(project_name)
```

**Why?**
- **Testable** - You can test `Deployer` without CLI
- **Reusable** - Logic can be used outside CLI
- **Maintainable** - Separation of concerns
- **Clean** - CLI file stays small and focused

## Running Shared Subcommands

### Using the CLI

```bash
# Run a shared command
$ uv run my-awesome-project version
my-awesome-project version 1.0.0

# Get help for a shared command
$ uv run my-awesome-project deploy --help
Usage: my-awesome-project deploy [OPTIONS]

  Deploy the application to production.

Options:
  --help  Show this message and exit.

# List all available commands (including shared ones)
$ uv run my-awesome-project --help
```

### Programmatically

You can also call shared subcommands programmatically:

```python
from company_base.dev.cli.shared_subcommands import deploy

# Call the function directly
deploy()
```

## Multi-Package Example

Here's a complete example of shared commands across packages:

```
pyrig (base framework)
  └── dev/cli/shared_subcommands.py
      └── version()  # Available in ALL packages

company-base (your organization's base)
  └── dev/cli/shared_subcommands.py
      ├── deploy()
      ├── security_scan()
      └── lint_all()  # Available in all company packages

service-a (depends on company-base)
  └── dev/cli/
      ├── shared_subcommands.py  # Empty or has service-a specific shared commands
      └── subcommands.py
          └── migrate()  # Only in service-a
```

When you run `uv run service-a --help`:

**Shared commands (from dependencies):**
- `version` (from pyrig)
- `deploy` (from company-base)
- `security-scan` (from company-base)
- `lint-all` (from company-base)

**Project-specific commands:**
- `migrate` (from service-a's subcommands.py)

## Customization

You can add imports or utilities to the `shared_subcommands.py`:

### Example: Export Shared Commands

```python
# company_base/dev/cli/shared_subcommands.py
"""Shared commands for the CLI."""

import typer


def deploy() -> None:
    """Deploy the application."""
    typer.echo("Deploying...")


def rollback() -> None:
    """Rollback the last deployment."""
    typer.echo("Rolling back...")


# Export for programmatic use
__all__ = ["deploy", "rollback"]
```

### Example: Shared Utilities

```python
# company_base/dev/cli/shared_subcommands.py
"""Shared commands for the CLI."""

import typer
from pathlib import Path


def _get_project_root() -> Path:
    """Get the project root directory."""
    return Path.cwd()


def _confirm_production() -> bool:
    """Confirm production deployment."""
    return typer.confirm("Deploy to PRODUCTION?")


def deploy() -> None:
    """Deploy the application."""
    if _confirm_production():
        root = _get_project_root()
        typer.echo(f"Deploying from {root}...")
```

## Related Files

- **`{package_name}/dev/cli/__init__.py`** - CLI package init (created by pyrig)
- **`{package_name}/dev/cli/subcommands.py`** - Project-specific commands ([subcommands.md](subcommands.md))
- **`{package_name}/dev/cli/cli.py`** - CLI entry point (in pyrig only)

## Common Issues

### Issue: Shared command not discovered

**Symptom:** Custom shared command not available in dependent packages

**Cause:** Package not installed or not in dependency graph

**Solution:**
```bash
# Ensure base package is installed
uv add company-base

# Verify it's in the dependency graph
uv run python -c "
from pyrig.src.modules.package import DependencyGraph
graph = DependencyGraph()
deps = graph.get_all_depending_on('pyrig')
print([d.__name__ for d in deps])
"

# Should show: ['company_base', 'my_app', ...]

# Re-run to refresh
uv run my-app --help
```

### Issue: Command conflicts between packages

**Symptom:** Two packages define the same shared command

**Cause:** Multiple packages in the dependency chain define the same function

**Solution:**
```python
# In the derived package, use a different name or don't define it
# The command from the base package will be used

# If you need to override, use a more specific name:
# company_base/dev/cli/shared_subcommands.py
def deploy() -> None:
    """Deploy (base implementation)."""
    pass

# my_app/dev/cli/shared_subcommands.py
def deploy_custom() -> None:
    """Deploy with custom logic."""
    pass
```

### Issue: Want to use shared command logic in subcommands

**Symptom:** Need to call shared command from project-specific command

**Cause:** Trying to import from shared_subcommands

**Solution:**
```python
# DON'T import from shared_subcommands - put logic in src/

# company_base/src/deployment/deployer.py
class Deployer:
    def deploy(self) -> None:
        """Deployment logic."""
        pass

# company_base/dev/cli/shared_subcommands.py
def deploy() -> None:
    """Deploy command."""
    from company_base.src.deployment.deployer import Deployer
    Deployer().deploy()

# my_app/dev/cli/subcommands.py
def deploy_with_migration() -> None:
    """Deploy with migration."""
    # Import the logic, not the command
    from company_base.src.deployment.deployer import Deployer

    # Run migration first
    _run_migration()

    # Then deploy
    Deployer().deploy()
```

## Best Practices

### ✅ DO

- **Use for organization-wide commands** - Commands all projects need
- **Keep logic in src/** - Use shared_subcommands.py only as wrapper
- **Use descriptive names** - `deploy`, `security-scan`, not `cmd1`
- **Add docstrings** - They become help text
- **Test your commands** - Ensure they work across packages
- **Version your base package** - Use semantic versioning

### ❌ DON'T

- **Don't put business logic here** - Keep it in src/
- **Don't create command conflicts** - Use unique names
- **Don't hardcode project names** - Use `get_project_name_from_argv()`
- **Don't make commands stateful** - Keep them simple
- **Don't forget to document** - Explain what each command does

## Advanced Usage

### Command with Configuration

```python
# company_base/dev/cli/shared_subcommands.py
"""Shared commands for the CLI."""

import typer
from pathlib import Path
import tomli


def deploy(
    environment: str = typer.Option("production", help="Target environment"),
    dry_run: bool = typer.Option(False, help="Perform a dry run"),
) -> None:
    """Deploy the application."""
    # Load project config
    config = _load_config()

    if dry_run:
        typer.echo(f"[DRY RUN] Would deploy to {environment}")
    else:
        typer.echo(f"Deploying to {environment}...")
        # Deployment logic


def _load_config() -> dict:
    """Load project configuration."""
    config_file = Path("pyproject.toml")
    with config_file.open("rb") as f:
        return tomli.load(f)
```

### Command with Progress

```python
# company_base/dev/cli/shared_subcommands.py
"""Shared commands for the CLI."""

import typer
import time


def build_all() -> None:
    """Build all artifacts."""
    steps = ["Linting", "Type checking", "Testing", "Building"]

    with typer.progressbar(steps, label="Building") as progress:
        for step in progress:
            typer.echo(f"  {step}...")
            time.sleep(1)  # Your actual build step here

    typer.echo("✅ Build complete!")
```

### Command with Rich Output

```python
# company_base/dev/cli/shared_subcommands.py
"""Shared commands for the CLI."""

import typer
from rich.console import Console
from rich.table import Table


def status() -> None:
    """Show project status."""
    console = Console()

    table = Table(title="Project Status")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="magenta")

    table.add_row("Tests", "✅ Passing")
    table.add_row("Coverage", "✅ 95%")
    table.add_row("Linting", "✅ Clean")

    console.print(table)
```

## See Also

- [Subcommands Documentation](subcommands.md) - Project-specific CLI commands
- [Multi-Package Architecture](../multi-package-architecture.md) - Cross-package discovery
- [Getting Started Guide](../getting-started.md) - Initial project setup
- [Typer Documentation](https://typer.tiangolo.com/) - CLI framework used by pyrig




