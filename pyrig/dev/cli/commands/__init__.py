"""CLI command implementations for pyrig.

This package contains the implementation functions for pyrig's CLI commands.
Each module provides the core logic for a specific command, which is then
wrapped by a thin CLI interface in `pyrig.dev.cli.subcommands`.

Commands:
    - `init_project`: Complete project initialization sequence
    - `create_root`: Generate project structure and config files
    - `create_tests`: Generate test skeletons for source code
    - `make_inits`: Create missing __init__.py files
    - `build_artifacts`: Build all distributable artifacts
    - `protect_repo`: Configure GitHub repository protection

The separation between command implementation and CLI interface allows:
- Testing command logic independently of CLI framework
- Reusing command logic programmatically
- Keeping CLI definitions clean and focused on argument parsing

Example:
    >>> from pyrig.dev.cli.commands.create_tests import make_test_skeletons
    >>> # Call command logic directly without CLI
    >>> make_test_skeletons()
"""
