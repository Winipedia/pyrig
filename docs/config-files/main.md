# MainConfigFile

## Overview

**File Location:** `{package_name}/main.py`
**ConfigFile Class:** `MainConfigFile`
**File Type:** Python
**Priority:** Standard

Creates the main entry point for your application. This file contains the `main()` function that serves as the primary entry point for your CLI and can be run directly with Python.

## Purpose

The `{package_name}/main.py` file provides the application entry point:

- **CLI Entry Point** - Main function called by CLI commands
- **Direct Execution** - Can be run with `python -m {package_name}.main`
- **Extensibility** - You can add your application logic here
- **Standard Pattern** - Follows Python best practices
- **Clean Separation** - Separates entry point from CLI framework

### Why pyrig manages this file

pyrig creates `main.py` to:
1. **Immediate functionality** - Working entry point from day one
2. **Standard structure** - Follows Python conventions
3. **CLI integration** - Connects to Typer CLI framework
4. **Flexibility** - You can customize the main function
5. **Clean architecture** - Separates concerns (main logic vs CLI framework)

The file is created during `pyrig init` by copying the entire content from pyrig's `main.py` module.

## File Location

The file is placed in your package's root directory:

```
my-awesome-project/
├── my_awesome_project/
│   ├── __init__.py
│   ├── main.py  # <-- Here
│   ├── dev/
│   │   └── cli/
│   │       ├── cli.py
│   │       └── subcommands.py
│   └── src/
└── pyproject.toml
```

This mirrors pyrig's structure:

```
pyrig/
├── pyrig/
│   ├── __init__.py
│   ├── main.py  # <-- Copied from here
│   ├── dev/
│   │   └── cli/
│   │       ├── cli.py
│   │       └── subcommands.py
│   └── src/
└── pyproject.toml
```

**Note:** pyrig automatically deletes any root-level `main.py` (at project root) to ensure the main file is in the package directory.

## File Structure

### Complete Module Copy

The file contains the **complete content** from pyrig's `main.py`:

```python
"""Main entrypoint for the project."""


def main() -> None:
    """Main entrypoint for the project."""


if __name__ == "__main__":
    main()
```

### Components

#### Module Docstring

```python
"""Main entrypoint for the project."""
```

- **Type:** Module docstring
- **Default:** Copied from `pyrig.main`
- **Required:** Yes
- **Purpose:** Documents the module
- **Why pyrig sets it:** Provides context

#### main() Function

```python
def main() -> None:
    """Main entrypoint for the project."""
```

- **Type:** Function definition
- **Default:** Empty function body
- **Required:** Yes (for CLI to work)
- **Purpose:** Application entry point
- **Why pyrig sets it:** CLI framework calls this function

**Important:** This function is called by the CLI framework defined in `pyproject.toml`.

#### __main__ Guard

```python
if __name__ == "__main__":
    main()
```

- **Type:** Conditional execution
- **Default:** Calls `main()` when run directly
- **Required:** Yes (for validation)
- **Purpose:** Allows direct execution with `python -m`
- **Why pyrig sets it:** Standard Python pattern

## Default Configuration

For a project named `my-awesome-project` with package `my_awesome_project`:

**File location:** `my_awesome_project/main.py`

**File contents:**
```python
"""Main entrypoint for the project."""


def main() -> None:
    """Main entrypoint for the project."""


if __name__ == "__main__":
    main()
```

## How It Works

### CLI Integration

The `main()` function is registered as a CLI command in `pyproject.toml`:

```toml
[project.scripts]
my-awesome-project = "my_awesome_project.dev.cli.cli:main"
```

The CLI framework (`dev/cli/cli.py`) automatically discovers and registers the `main()` function:

```python
# In dev/cli/cli.py
from pyrig import main as pyrig_main

# Replace pyrig with your package name
main_module_name = get_module_name_replacing_start_module(pyrig_main, pkg_name)
main_module = import_module_from_path(main_module_name)
app.command()(main_module.main)  # Register main() as a command
```

### Execution Flow

```
User runs: uv run my-awesome-project
    ↓
pyproject.toml [project.scripts] entry point
    ↓
my_awesome_project.dev.cli.cli:main
    ↓
CLI framework discovers and registers commands
    ↓
Calls my_awesome_project.main:main()
    ↓
Your application logic executes
```

### Direct Execution

You can also run the main file directly:

```bash
# Run as module
python -m my_awesome_project.main

# Or with uv
uv run python -m my_awesome_project.main
```

## Customization

You can add your application logic to the `main()` function:

### Example: Simple Application

```python
"""Main entrypoint for the project."""


def main() -> None:
    """Main entrypoint for the project."""
    print("Welcome to my-awesome-project!")
    print("Running main application logic...")


if __name__ == "__main__":
    main()
```

```bash
$ uv run my-awesome-project
Welcome to my-awesome-project!
Running main application logic...
```

### Example: Application with Configuration

```python
"""Main entrypoint for the project."""

from pathlib import Path
import json


def load_config() -> dict:
    """Load application configuration."""
    config_path = Path.home() / ".my-awesome-project" / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {"debug": False}


def main() -> None:
    """Main entrypoint for the project."""
    config = load_config()

    if config.get("debug"):
        print("Debug mode enabled")

    print("Application started")
    # Your application logic here


if __name__ == "__main__":
    main()
```

### Example: Application with Error Handling

```python
"""Main entrypoint for the project."""

import sys
import logging


def setup_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main() -> None:
    """Main entrypoint for the project."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("Application starting")
        # Your application logic here
        logger.info("Application completed successfully")
    except Exception as e:
        logger.exception("Application failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Example: Application with Submodules

```python
"""Main entrypoint for the project."""

from my_awesome_project.core import run_application
from my_awesome_project.config import load_settings


def main() -> None:
    """Main entrypoint for the project."""
    # Load settings
    settings = load_settings()

    # Run the application
    run_application(settings)


if __name__ == "__main__":
    main()
```

## Validation

pyrig validates that `main.py` has the required structure:

### Required Elements

1. **main() function** - Must contain `def main`
2. **__main__ guard** - Must contain `if __name__ == "__main__":`

### Flexible Validation

pyrig allows modifications as long as these elements exist:

```python
# Valid: Custom implementation
"""Main entrypoint for the project."""

import sys


def main() -> None:
    """Main entrypoint for the project."""
    print("Custom logic here")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

```python
# Valid: Additional functions
"""Main entrypoint for the project."""


def setup() -> None:
    """Setup function."""
    pass


def main() -> None:
    """Main entrypoint for the project."""
    setup()


if __name__ == "__main__":
    main()
```

```python
# Invalid: Missing main() function
"""Main entrypoint for the project."""


def run() -> None:  # Wrong name
    """Run the application."""
    pass


if __name__ == "__main__":
    run()
```

```python
# Invalid: Missing __main__ guard
"""Main entrypoint for the project."""


def main() -> None:
    """Main entrypoint for the project."""
    pass

# Missing: if __name__ == "__main__": main()
```

## Root-Level main.py Cleanup

pyrig automatically deletes any `main.py` file at the project root:

```
my-awesome-project/
├── main.py  # <-- This will be deleted
├── my_awesome_project/
│   └── main.py  # <-- This is the correct location
└── pyproject.toml
```

**Why:** The main file should be in the package directory, not the project root. This ensures proper module structure and import paths.

## Container Integration

The `main.py` is used as the default command in containers:

```dockerfile
# Containerfile
FROM python:3.12-slim
# ... setup ...
ENTRYPOINT ["uv", "run", "my-awesome-project"]
CMD ["main"]  # <-- Calls main() function
```

This allows running the container without arguments:

```bash
$ podman run my-awesome-project
# Executes: uv run my-awesome-project main
```

## Related Files

- **`{package_name}/dev/cli/cli.py`** - CLI framework that registers main()
- **`{package_name}/dev/cli/subcommands.py`** - Additional CLI commands ([subcommands.md](subcommands.md))
- **`pyproject.toml`** - Defines CLI entry point ([pyproject.md](pyproject.md))
- **`tests/test_{package_name}/test_main.py`** - Tests for main() ([main-test.md](main-test.md))
- **`Containerfile`** - Container configuration ([container-file.md](container-file.md))

## Common Issues

### Issue: CLI command not found

**Symptom:** `command not found: my-awesome-project`

**Cause:** Package not installed or entry point not configured

**Solution:**
```bash
# Install the package
uv sync

# Or run with uv
uv run my-awesome-project
```

### Issue: main() not called

**Symptom:** Nothing happens when running the CLI

**Cause:** Empty main() function

**Solution:**
```python
def main() -> None:
    """Main entrypoint for the project."""
    print("Application started")  # Add your logic
```

### Issue: Import errors in main()

**Symptom:** `ModuleNotFoundError` when running main

**Cause:** Incorrect import paths

**Solution:**
```python
# Use absolute imports from your package
from my_awesome_project.core import run_application  # Good
from core import run_application  # Bad (relative import)
```

### Issue: Want to pass arguments to main()

**Symptom:** How to accept CLI arguments in main()?

**Cause:** main() is registered as a Typer command

**Solution:**

Use Typer's argument/option syntax:

```python
"""Main entrypoint for the project."""

import typer


def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    config: str = typer.Option("config.json", help="Config file path"),
) -> None:
    """Main entrypoint for the project."""
    if verbose:
        print(f"Loading config from {config}")
    # Your logic here


if __name__ == "__main__":
    main()
```

```bash
$ uv run my-awesome-project --verbose --config custom.json
Loading config from custom.json
```

### Issue: Want different behavior for direct execution

**Symptom:** Need different behavior when run with `python -m`

**Cause:** Same code path for CLI and direct execution

**Solution:**

```python
"""Main entrypoint for the project."""

import sys


def main(verbose: bool = False) -> None:
    """Main entrypoint for the project."""
    if verbose:
        print("Verbose mode enabled")
    print("Application running")


if __name__ == "__main__":
    # Direct execution: parse arguments manually
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    main(verbose=verbose)
```

## Best Practices

### ✅ DO

- **Keep main() simple** - Delegate to other modules
- **Use absolute imports** - Import from your package
- **Add error handling** - Catch and log exceptions
- **Return exit codes** - Use `sys.exit()` for errors
- **Add logging** - Use Python's logging module

### ❌ DON'T

- **Don't put all logic in main()** - Use separate modules
- **Don't use relative imports** - Use absolute imports
- **Don't ignore errors** - Handle exceptions properly
- **Don't hardcode paths** - Use Path and config files
- **Don't skip the __main__ guard** - Required for validation

## Advanced Usage

### Application with Dependency Injection

```python
"""Main entrypoint for the project."""

from my_awesome_project.container import Container
from my_awesome_project.app import Application


def main() -> None:
    """Main entrypoint for the project."""
    # Setup dependency injection
    container = Container()
    container.wire(modules=[__name__])

    # Create and run application
    app = Application(container)
    app.run()


if __name__ == "__main__":
    main()
```

### Application with Async Support

```python
"""Main entrypoint for the project."""

import asyncio
from my_awesome_project.async_app import run_async_application


def main() -> None:
    """Main entrypoint for the project."""
    asyncio.run(run_async_application())


if __name__ == "__main__":
    main()
```

### Application with Signal Handling

```python
"""Main entrypoint for the project."""

import signal
import sys


def signal_handler(sig, frame) -> None:
    """Handle shutdown signals."""
    print("\nShutting down gracefully...")
    sys.exit(0)


def main() -> None:
    """Main entrypoint for the project."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Application running (Ctrl+C to stop)")

    # Your application logic
    while True:
        pass


if __name__ == "__main__":
    main()
```

## See Also

- [Typer Documentation](https://typer.tiangolo.com/) - CLI framework
- [Python Entry Points](https://packaging.python.org/en/latest/specifications/entry-points/) - Official spec
- [subcommands.py](subcommands.md) - Additional CLI commands
- [pyproject.toml](pyproject.md) - CLI configuration
- [test_main.py](main-test.md) - Main entry point tests
- [Getting Started Guide](../getting-started.md) - Initial project setup


