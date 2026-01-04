"""CLI entry point and dynamic command registration system.

Implements the main CLI entry point for pyrig and all pyrig-based projects with
dynamic command discovery and registration from multiple sources across the
package dependency chain.

Built on Typer with pyrig's multi-package architecture for extensibility.
Projects depending on pyrig can define their own commands that are automatically
discovered and integrated.

Command Discovery:
    Discovers and registers commands from three sources:
    1. Main entry point: `main()` from `<package>.main`
    2. Project-specific commands: Functions from `<package>.dev.cli.subcommands`
    3. Shared commands: Functions from `<package>.dev.cli.shared_subcommands`
       across all packages in the dependency chain

Logging Configuration:
    Flexible logging control through global options:
    - Default: INFO level with clean formatting
    - `-q/--quiet`: WARNING level (errors and warnings only)
    - `-v`: DEBUG level with level prefix
    - `-vv`: DEBUG level with module names
    - `-vvv`: DEBUG level with timestamps and full details

Example:
    $ uv run pyrig init
    $ uv run pyrig -v mkroot  # Debug output
    $ uv run myproject deploy  # Custom command in dependent project
"""

import logging
from importlib import import_module

import typer

import pyrig
from pyrig import main as pyrig_main
from pyrig.dev.cli import shared_subcommands, subcommands
from pyrig.src.cli import get_pkg_name_from_argv
from pyrig.src.modules.function import get_all_functions_from_module
from pyrig.src.modules.module import (
    get_module_name_replacing_start_module,
    import_module_with_file_fallback,
)
from pyrig.src.modules.package import discover_equivalent_modules_across_dependents
from pyrig.src.modules.path import ModulePath

logger = logging.getLogger(__name__)

app = typer.Typer(no_args_is_help=True)
"""Main Typer application instance.

Root Typer app that all commands are registered to. Configured with
`no_args_is_help=True` to display help when invoked without a command.
"""


@app.callback()
def configure_logging(
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        help="Increase verbosity: -v (DEBUG), -vv (modules), -vvv (timestamps)",
    ),
    quiet: bool = typer.Option(  # noqa: FBT001
        False,  # noqa: FBT003
        "--quiet",
        "-q",
        help="Only show warnings and errors",
    ),
) -> None:
    """Configure logging based on verbosity flags.

    Typer callback that runs before any command executes. Configures the Python
    logging system based on user-provided verbosity flags.

    Logging Levels:
        - Default: INFO level, clean formatting (just messages)
        - `-q/--quiet`: WARNING level (only warnings and errors)
        - `-v`: DEBUG level with level prefix
        - `-vv`: DEBUG level with module names
        - `-vvv+`: DEBUG level with timestamps and full details

    Args:
        verbose: Verbosity level from number of `-v` flags (0=INFO, 1=DEBUG,
            2=DEBUG with modules, 3+=DEBUG with timestamps). Count option.
        quiet: If True, sets WARNING level. Takes precedence over verbose.

    Note:
        Uses `force=True` in `logging.basicConfig()` to override existing config.
    """
    if quiet:
        # --quiet: only show warnings and errors
        level = logging.WARNING
        fmt = "%(levelname)s: %(message)s"
    elif verbose == 0:
        # Default: show info messages with clean formatting
        level = logging.INFO
        fmt = "%(message)s"
    elif verbose == 1:
        # -v: show debug messages with level prefix
        level = logging.DEBUG
        fmt = "%(levelname)s: %(message)s"
    elif verbose == 2:  # noqa: PLR2004
        # -vv: show debug messages with module names
        level = logging.DEBUG
        fmt = "%(levelname)s [%(name)s] %(message)s"
    else:
        # -vvv+: show debug messages with timestamps and full details
        level = logging.DEBUG
        fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"

    logging.basicConfig(level=level, format=fmt, force=True)


def add_subcommands() -> None:
    """Discover and register project-specific CLI commands.

    Dynamically discovers and registers two types of commands:
    1. Main entry point: `main()` from `<package>.main`
    2. Subcommands: All functions from `<package>.dev.cli.subcommands`

    Discovery Process:
        1. Extracts package name from `sys.argv[0]`
        2. Replaces root module name in pyrig's paths with current package
        3. Converts module names to file paths and imports with fallback
        4. Extracts all functions from subcommands module
        5. Registers each function as a Typer command

    This enables dependent projects to define their own commands by creating
    `<package>.dev.cli.subcommands` with functions.

    Example:
        # myproject/dev/cli/subcommands.py
        def deploy() -> None:
            '''Deploy the application.'''
            ...

        $ uv run myproject deploy

    Note:
        Package name is extracted from `sys.argv[0]`, not working directory.
        Only functions defined in the module are registered (imported functions
        are excluded).
    """
    # extract project name from sys.argv[0]
    pkg_name = get_pkg_name_from_argv()
    logger.debug("Registering subcommands for package: %s", pkg_name)

    main_module_name = get_module_name_replacing_start_module(pyrig_main, pkg_name)
    main_module_path = ModulePath.module_name_to_relative_file_path(main_module_name)
    main_module = import_module_with_file_fallback(main_module_path)
    app.command()(main_module.main)

    # replace the first parent with pkg_name
    subcommands_module_name = get_module_name_replacing_start_module(
        subcommands, pkg_name
    )
    subcommands_module_path = ModulePath.module_name_to_relative_file_path(
        subcommands_module_name
    )

    subcommands_module = import_module_with_file_fallback(subcommands_module_path)

    sub_cmds = get_all_functions_from_module(subcommands_module)

    for sub_cmd in sub_cmds:
        logger.debug("Registering subcommand: %s", sub_cmd.__name__)  # ty:ignore[unresolved-attribute]
        app.command()(sub_cmd)


def add_shared_subcommands() -> None:
    """Discover and register shared CLI commands from the dependency chain.

    Discovers and registers shared commands available across all pyrig-based
    projects. Commands are defined in `<package>.dev.cli.shared_subcommands`
    modules and automatically available in all dependent projects.

    Discovery Process:
        1. Extracts current package name from `sys.argv[0]`
        2. Imports current package
        3. Finds all packages in dependency chain from pyrig to current package
        4. For each package, looks for `dev.cli.shared_subcommands` module
        5. Extracts all public functions from each module
        6. Registers each function as a Typer command

    This enables creating commands that work consistently across an ecosystem
    while adapting to each project's context. For example, the `version` command
    displays the version of the project being run, not pyrig's version.

    Example:
        $ uv run pyrig version
        pyrig version 3.1.5

        $ uv run myproject version
        myproject version 1.2.3

    Note:
        Commands are registered in dependency order (pyrig first). If multiple
        packages define the same command name, the last one registered takes
        precedence.
    """
    package_name = get_pkg_name_from_argv()
    package = import_module(package_name)
    all_shared_subcommands_modules = discover_equivalent_modules_across_dependents(
        shared_subcommands,
        pyrig,
        until_pkg=package,
    )
    for shared_subcommands_module in all_shared_subcommands_modules:
        logger.debug(
            "Registering shared subcommands from module: %s",
            shared_subcommands_module.__name__,
        )
        sub_cmds = get_all_functions_from_module(shared_subcommands_module)
        for sub_cmd in sub_cmds:
            logger.debug("Registering shared subcommand: %s", sub_cmd.__name__)  # ty:ignore[unresolved-attribute]
            app.command()(sub_cmd)


def main() -> None:
    """Main entry point for the pyrig CLI.

    Primary entry point called when the CLI is invoked (e.g., `uv run pyrig <command>`).
    Orchestrates command discovery and registration before invoking the Typer app.

    Steps:
        1. Discovers and registers project-specific commands
        2. Discovers and registers shared commands
        3. Invokes Typer app to parse arguments and execute command

    Registered as a console script entry point in pyproject.toml.

    Example:
        $ uv run pyrig mkroot

        This function:
        1. Discovers pyrig's main() and subcommands
        2. Discovers shared commands (version, etc.)
        3. Invokes Typer to parse and execute mkroot

    Note:
        Called automatically by console script entry point. Takes no arguments;
        all CLI arguments are parsed by Typer. Logging is configured by the
        `configure_logging` callback before command execution.
    """
    add_subcommands()
    add_shared_subcommands()
    app()
