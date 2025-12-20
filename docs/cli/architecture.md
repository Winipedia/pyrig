# CLI Architecture

The pyrig CLI uses dynamic command discovery to automatically register commands from module functions. This enables both pyrig's built-in commands and project-specific commands in packages that depend on pyrig.

## Entry Point

Commands are invoked through the console script entry point defined in `pyproject.toml`:

```toml
[project.scripts]
pyrig = "pyrig.dev.cli.cli:main"
```

Running `uv run pyrig <command>` calls the `main()` function in `pyrig/dev/cli/cli.py`.

## Command Registration Flow

The `main()` function orchestrates command discovery in three steps:

```python
def main() -> None:
    add_subcommands()           # Register project-specific commands
    add_shared_subcommands()    # Register shared commands
    app()                       # Execute Typer application
```

```mermaid
graph LR
    A[uv run pyrig init] --> B[main]
    B --> C[add_subcommands]
    B --> D[add_shared_subcommands]
    B --> E[app]
    E --> F[Execute init]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style D fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style E fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style F fill:#9d84b7,stroke:#333,stroke-width:2px,color:#000
```

### Project-Specific Commands

The `add_subcommands()` function discovers commands for the current package:

1. **Extract package name** from `sys.argv[0]`
2. **Replace module names** to find the package's equivalent modules
3. **Import the subcommands module** for the package
4. **Extract all functions** from the module
5. **Register each function** as a Typer command

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#a8dadc','primaryTextColor':'#000','primaryBorderColor':'#333','lineColor':'#333','secondaryColor':'#90be6d','tertiaryColor':'#f4a261','actorBkg':'#a8dadc','actorBorder':'#333','actorTextColor':'#000','signalColor':'#333','signalTextColor':'#000'}}}%%
sequenceDiagram
    participant CLI as add_subcommands()
    participant Argv as sys.argv[0]
    participant Replace as Module Replacement
    participant Import as Import System
    participant Typer as Typer App

    CLI->>Argv: Extract package name
    Argv-->>CLI: "myapp"
    CLI->>Replace: Replace pyrig → myapp
    Replace-->>CLI: myapp.dev.cli.subcommands
    CLI->>Import: Import module
    Import-->>CLI: [init, mkroot, build, ...]
    CLI->>Typer: Register each function
```

Example: When running `uv run myapp init`, the system:
- Detects package name: `myapp`
- Replaces `pyrig.dev.cli.subcommands` → `myapp.dev.cli.subcommands`
- Imports `myapp/dev/cli/subcommands.py`
- Registers all functions as commands

### Shared Commands

The `add_shared_subcommands()` function discovers commands across the package ecosystem:

1. **Build a dependency graph** of all installed packages
2. **Find all packages** that depend on pyrig
3. **For each package**, import its `shared_subcommands` module
4. **Register all functions** from each module

This enables commands like `version` to work in any package that depends on pyrig.

## Module Name Replacement

The system uses module name replacement to support multi-package architectures:

```python
get_module_name_replacing_start_module(pyrig.dev.cli.subcommands, "myapp")
# Returns: "myapp.dev.cli.subcommands"
```

This allows any package depending on pyrig to define its own commands by following the same module structure.

## Dependency Graph

The `DependencyGraph` class builds a directed graph of package dependencies:

```python
graph = DependencyGraph()
packages = graph.get_all_depending_on("pyrig", include_self=True)
# Returns: [pyrig, myapp, myplugin] in topological order
```

```mermaid
graph TD
    A[pyrig] --> B[myapp]
    B --> C[myplugin]
    A --> D[another-pkg]

    A:::base
    B:::dep1
    C:::dep2
    D:::dep1

    classDef base fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    classDef dep1 fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    classDef dep2 fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
```

This enables discovery of all packages in the pyrig ecosystem and their corresponding command modules.

## Function Discovery

The `get_all_functions_from_module()` utility extracts all functions defined in a module:

- Uses `inspect.getmembers()` to find all module members
- Filters to only callable functions
- Excludes imported functions (only functions defined in the module)
- Sorts by definition order (line number)

```mermaid
flowchart LR
    A[Module] --> B[inspect.getmembers]
    B --> C{Is callable?}
    C -->|No| D[Skip]
    C -->|Yes| E{Defined in module?}
    E -->|No| D
    E -->|Yes| F[Add to list]
    F --> G[Sort by line number]
    G --> H[Return functions]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style D fill:#ccc,stroke:#333,stroke-width:2px,color:#000
    style E fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style F fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style G fill:#9d84b7,stroke:#333,stroke-width:2px,color:#000
    style H fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
```

This automatic discovery means adding a new command requires only defining a function in the appropriate module.

## Import Strategy

The system uses a fallback import strategy for robustness:

1. **Try normal import** by module name
2. **Fall back to file-based import** if the module isn't in `sys.path`

This handles edge cases where modules may not be properly installed or are in development mode. Mainly can be important when files are created during init and are not seen by normal imports yet.

## Command Execution

Once registered, Typer handles argument parsing and command execution:

```mermaid
graph TD
    A[uv run pyrig init] --> B[Entry point: pyrig.dev.cli.cli:main]
    B --> C[Register all commands]
    C --> D[Typer parses 'init' argument]
    D --> E[Execute init function]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style D fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style E fill:#9d84b7,stroke:#333,stroke-width:2px,color:#000
```

The function's docstring becomes the command's help text, and Typer automatically generates argument parsing from the function signature.

You will not be building a crazy CLI package with this or an cli based application, but it comes quite in handy for building a CLI for your project and have some simple commands that can be executed from the command line because lets be honest no one like doing `python -m myapp.subpkg.subpkg2.module` instead of `uv run myapp init`. Also you dont need the classic `if __name__ == "__main__":` boilerplate anymore this way.

