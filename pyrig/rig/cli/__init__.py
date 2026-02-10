"""Command-line interface package for pyrig.

Provides complete CLI infrastructure for pyrig and pyrig-based projects with
dynamic command discovery from multiple sources:

1. Project-specific commands from `<package>.dev.cli.subcommands`
2. Shared commands from `<package>.dev.cli.shared_subcommands` across the
   dependency chain
3. Main entry point from `<package>.main`

Built on Typer with automatic command discovery through pyrig's multi-package
architecture, enabling dependent projects to define their own commands that are
automatically integrated.

Modules:
    cli: Main entry point, command registration, and Typer app
    subcommands: Project-specific command wrappers
    shared_subcommands: Shared commands across all pyrig-based projects
    commands: Command implementation functions (separate from CLI interface)
"""
