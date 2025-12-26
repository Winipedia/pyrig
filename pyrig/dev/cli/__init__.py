"""Command-line interface package for pyrig.

This package provides the complete CLI infrastructure for pyrig and pyrig-based
projects. It implements a dynamic command discovery system that automatically
registers commands from multiple sources:

1. **Project-specific commands** from `<package>.dev.cli.subcommands`
2. **Shared commands** from `<package>.dev.cli.shared_subcommands` across all
   packages in the dependency chain
3. **Main entry point** from `<package>.main`

The CLI is built on Typer and supports automatic command discovery through
pyrig's multi-package architecture, enabling projects that depend on pyrig to
define their own commands that are automatically integrated into the CLI.

Modules:
    cli: Main CLI entry point, command registration, and Typer app configuration
    subcommands: Project-specific CLI command wrappers for pyrig
    shared_subcommands: Shared commands available across all pyrig-based projects
    commands: Implementation functions for CLI commands (separate from CLI interface)

Example:
    Running pyrig commands::

        $ uv run pyrig init
        $ uv run pyrig mkroot
        $ uv run pyrig build
        $ uv run pyrig version

    Running commands in a project that depends on pyrig::

        $ uv run myproject deploy  # Custom command from myproject.dev.cli.subcommands
        $ uv run myproject version  # Shared command from pyrig

See Also:
    pyrig.dev.cli.cli.main: CLI entry point function
    pyrig.dev.cli.cli.add_subcommands: Project-specific command discovery
    pyrig.dev.cli.cli.add_shared_subcommands: Shared command discovery
"""
