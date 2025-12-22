# Subcommands

Project-specific CLI commands are defined in the `dev/cli/subcommands.py` module. All functions in this module are automatically registered as CLI commands.

## Defining Commands

Add a function to `subcommands.py` to create a new command:

```python
import typer

def mkroot(
    *,
    priority: bool = typer.Option(
        default=False,
        help="Only create priority config files.",
    ),
) -> None:
    """Creates the root of the project.

    This inits all ConfigFiles and creates __init__.py files for the src
    and tests package where they are missing. It does not overwrite any
    existing files.
    """
    # local imports in pyrig to avoid cli failure when installing without dev deps
    # as some pyrig commands are dependend on dev deps and can only be used in a dev env
    from pyrig.dev.cli.commands.create_root import make_project_root

    make_project_root(priority=priority)
```

The function name becomes the command name (converted to kebab-case), and the docstring becomes the help text.

### Adding Command-Line Arguments

Use `typer.Option` to add command-line arguments with flags:

```python
import typer

def deploy(
    *,
    environment: str = typer.Option(
        default="staging",
        help="Deployment environment (staging, production).",
    ),
    dry_run: bool = typer.Option(
        default=False,
        help="Perform a dry run without making changes.",
    ),
) -> None:
    """Deploy the application to the specified environment."""
    from myapp.dev.cli.commands.deploy import deploy_app

    deploy_app(environment=environment, dry_run=dry_run)
```

This creates a command with options:
```bash
uv run myapp deploy --environment production
uv run myapp deploy --dry-run
uv run myapp deploy --environment staging --dry-run
```

## Command Pattern

Follow this pattern for all subcommands:

1. **Define a simple wrapper function** in `subcommands.py`
2. **Use lazy imports** to avoid circular dependencies
3. **Delegate to implementation** in `dev/cli/commands/`
4. **Add comprehensive docstring** for CLI help

```mermaid
graph LR
    A[User runs command] --> B[subcommands.py wrapper]
    B --> C[Lazy import]
    C --> D[commands/ implementation]
    D --> E[Execute logic]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style D fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style E fill:#9d84b7,stroke:#333,stroke-width:2px,color:#000
```

Example:

```python
def build() -> None:
    """Build all artifacts.

    Invokes every subclass of Builder in the builder package.
    """
    from pyrig.dev.cli.commands.build_artifacts import build_artifacts

    build_artifacts()
```

## Automatic Registration

Functions are discovered and registered automatically:

- **No manual registration** required
- **Functions only** - classes and variables are ignored
- **Defined in module** - imported functions are excluded
- **Sorted by definition order** - commands appear in the order they're defined

Note: The main function from your main.py at myapp/main.py is automatically registered as a command as well in addition to all functions in subcommands.py.

### Discovery Process

```mermaid
graph TD
    A[CLI Entry Point] --> B[Extract package name from sys.argv]
    B --> C{Package is pyrig?}

    C -->|Yes| D[Import pyrig.dev.cli.subcommands]
    C -->|No| E[Replace module path with package name]
    E --> F[Import package.dev.cli.subcommands]

    D --> G[Get all functions from module]
    F --> G

    G --> H[Filter: only functions defined in module]
    H --> I[Sort by definition order]
    I --> J[For each function...]

    J --> K[Convert name to command name]
    K --> L[Register with Typer app]
    L --> J

    J --> M[All commands registered]
    M --> N[CLI ready to execute]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style D fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style E fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style F fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style G fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style H fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style I fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style K fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style L fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style N fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
```

## Command Naming

Function names are converted to CLI command names:

- `mkroot` → `pyrig mkroot`
- `mktests` → `pyrig mktests`
- `protect_repo` → `pyrig protect-repo`

## Multi-Package Support

When a package depends on pyrig, it can define its own subcommands:

```
myapp/
  dev/
    cli/
      subcommands.py  # Define myapp-specific commands here
```

```mermaid
graph TD
    A[pyrig/dev/cli/subcommands.py] -->|defines| B[pyrig commands]
    C[myapp/dev/cli/subcommands.py] -->|defines| D[myapp commands]

    E[uv run pyrig init] --> B
    F[uv run myapp deploy] --> D

    style A fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style D fill:#9d84b7,stroke:#333,stroke-width:2px,color:#000
```

Running `uv run myapp <command>` will discover and execute commands from `myapp.dev.cli.subcommands`.

## Built-in Commands

pyrig includes these built-in subcommands:

- **`init`** - Complete project setup
- **`mkroot`** - Create project structure and config files
- **`mktests`** - Generate test skeletons
- **`mkinits`** - Create `__init__.py` files
- **`build`** - Build all artifacts
- **`protect-repo`** - Configure repository protection
