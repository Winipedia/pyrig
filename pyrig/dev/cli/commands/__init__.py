"""CLI command implementation functions.

Core implementation logic for pyrig's CLI commands, separated from the CLI
interface layer for testability and reusability.

Architecture:
    Command implementations are separated from CLI wrappers in
    `pyrig.dev.cli.subcommands` to enable:
    - Independent testing without the CLI framework
    - Programmatic usage without CLI overhead
    - Lazy imports to avoid dev dependency errors

Modules:
    - `init_project`: Complete project initialization (9 steps)
    - `create_root`: Project structure and config file generation
    - `create_tests`: Test skeleton generation
    - `make_inits`: __init__.py file creation for namespace packages
    - `build_artifacts`: Artifact build orchestration
    - `protect_repo`: GitHub repository protection configuration

Note:
    Modules may import dev dependencies, so CLI wrappers use local imports
    to avoid errors when dev dependencies are not installed.
"""
