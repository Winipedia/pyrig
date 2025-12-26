"""CLI command implementation functions for pyrig.

This package contains the core implementation logic for pyrig's CLI commands.
Each module provides the actual functionality for a specific command, separated
from the CLI interface layer defined in `pyrig.dev.cli.subcommands`.

Architecture:
    The separation between command implementation (this package) and CLI
    interface (`pyrig.dev.cli.subcommands`) provides several benefits:

    - **Testability**: Implementation functions can be tested independently of
      the CLI framework (Typer)
    - **Reusability**: Command logic can be called programmatically without
      going through the CLI
    - **Clean interfaces**: CLI wrappers focus solely on argument parsing and
      validation
    - **Lazy imports**: Dev dependencies are imported only when commands execute,
      preventing import errors when pyrig is installed without dev dependencies

Modules:
    - `init_project`: Complete project initialization orchestration (9 steps)
    - `create_root`: Project structure and configuration file generation
    - `create_tests`: Test skeleton generation for all source code
    - `make_inits`: __init__.py file creation for namespace packages
    - `build_artifacts`: Artifact build orchestration via Builder discovery
    - `protect_repo`: GitHub repository protection and security configuration

Usage Pattern:
    Each module exports one or more implementation functions that are called
    by corresponding wrapper functions in `pyrig.dev.cli.subcommands`. The
    wrappers handle CLI argument parsing and then delegate to these
    implementations.

Example:
    Calling implementation functions directly (programmatic usage)::

        from pyrig.dev.cli.commands.create_tests import make_test_skeletons
        from pyrig.dev.cli.commands.create_root import make_project_root

        # Call command logic without CLI
        make_project_root(priority=True)
        make_test_skeletons()

    Calling via CLI (normal usage)::

        $ uv run pyrig mkroot --priority
        $ uv run pyrig mktests

Note:
    - All modules in this package may import dev dependencies, so they should
      only be imported when actually executing commands
    - The CLI wrappers in `pyrig.dev.cli.subcommands` use local imports to
      avoid import errors when dev dependencies are not installed

See Also:
    pyrig.dev.cli.subcommands: CLI wrapper functions that call these implementations
    pyrig.dev.cli.cli: Command discovery and registration system
"""
