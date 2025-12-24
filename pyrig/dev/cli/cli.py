"""CLI entry point and command registration.

This module provides the main CLI entry point for pyrig projects. It uses
Typer to build a command-line interface and automatically discovers
subcommands from the project's subcommands module.

The CLI supports both pyrig's built-in commands and project-specific
commands defined in the consuming project's subcommands module.

Example:
    $ uv run pyrig init
    $ uv run pyrig create-root
    $ uv run pyrig build
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
from pyrig.src.modules.package import get_same_modules_from_deps_depen_on_dep
from pyrig.src.modules.path import ModulePath

logger = logging.getLogger(__name__)

app = typer.Typer(no_args_is_help=True)
"""The main Typer application instance."""


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
    """Configure global CLI options.

    Args:
        verbose: Verbosity level (0=INFO, 1=DEBUG, 2=DEBUG with modules,
            3+=DEBUG with timestamps)
        quiet: If True, only show warnings and errors
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
    """Discover and register all CLI subcommands.

    Dynamically loads the main module and subcommands module for the
    current project, registering all public functions as CLI commands.
    This enables projects depending on pyrig to define their own commands.
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
    """Discover and register all shared CLI subcommands.

    This discovers all packages inheriting from pyrig and loads their
    shared_subcommands modules, registering all public functions as CLI
    commands. This enables cross-package commands that are available
    in all pyrig projects. Example is pyrigs version command that is
    available in all pyrig projects.
    So you can do:
        uv run pyrig version -> pyrig version 0.1.0
        uv run my-awesome-project version -> my-awesome-project version 0.1.0
    """
    package_name = get_pkg_name_from_argv()
    package = import_module(package_name)
    all_shared_subcommands_modules = get_same_modules_from_deps_depen_on_dep(
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
    """Entry point for the CLI.

    Registers all subcommands and invokes the Typer application.
    This function is called by the console script entry point.
    """
    add_subcommands()
    add_shared_subcommands()
    app()
