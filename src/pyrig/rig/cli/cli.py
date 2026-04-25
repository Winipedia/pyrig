"""CLI entry point and dynamic command registration for pyrig and pyrig-based projects.

Provides the main entry point with runtime command discovery from project-specific
and shared sources across the package dependency chain. Built on Typer.
"""

import logging
from importlib import import_module

import typer

import pyrig
from pyrig.core.cli import package_name_from_argv
from pyrig.core.introspection.dependencies import (
    discover_equivalent_modules_across_dependents,
)
from pyrig.core.introspection.functions import all_functions_from_module
from pyrig.core.introspection.modules import (
    import_module_with_default,
    module_name_replacing_start_module,
)
from pyrig.rig.cli import shared_subcommands, subcommands

app = typer.Typer(no_args_is_help=True)


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
    """Configure logging before any command executes.

    Typer callback that runs before every command. Adjusts the Python logging
    level and format based on the verbosity flags supplied by the user.

    Logging levels and formats:
        - Default (no flags): INFO, messages only.
        - ``-q``/``--quiet``: WARNING, ``LEVEL: message``.
        - ``-v``: DEBUG, ``LEVEL: message``.
        - ``-vv``: DEBUG, ``LEVEL [module] message``.
        - ``-vvv`` or more: DEBUG, ``timestamp LEVEL [module] message``.

    Args:
        verbose: Number of ``-v`` flags. 0 = INFO, 1 = DEBUG, 2 = DEBUG with
            module names, 3+ = DEBUG with timestamps. Count option.
        quiet: If ``True``, sets WARNING level. Takes precedence over verbose.

    Note:
        Uses ``force=True`` in ``logging.basicConfig`` to override any logging
        configuration already applied by imported modules.
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


def main() -> None:
    """Run the CLI application.

    Registers all project-specific and shared commands, then invokes the Typer
    app to parse arguments and dispatch the requested command. Called automatically
    by the console script entry point defined in ``pyproject.toml``.
    """
    add_subcommands()
    add_shared_subcommands()
    app()


def add_subcommands() -> None:
    """Discover and register project-specific commands from the calling package.

    Derives the calling package from ``sys.argv[0]``, constructs the module
    name ``<package>.rig.cli.subcommands``, and registers every function
    defined in that module as a Typer command.

    This allows any pyrig-based project to define its own CLI commands simply
    by adding functions to ``<package>.rig.cli.subcommands``.

    Example:
        # myproject/rig/cli/subcommands.py
        def deploy() -> None:
            '''Deploy the application.'''
            ...

        $ uv run myproject deploy

    Note:
        Only functions defined directly in the subcommands module are registered;
        imported functions are excluded. If the module cannot be imported,
        registration is silently skipped.
    """
    # extract project name from sys.argv[0]
    package_name = package_name_from_argv()
    # replace the first parent with package_name
    subcommands_module_name = module_name_replacing_start_module(
        subcommands, package_name
    )
    subcommands_module = import_module_with_default(subcommands_module_name)

    if subcommands_module is None:
        return

    sub_cmds = all_functions_from_module(subcommands_module)

    for sub_cmd in sub_cmds:
        app.command()(sub_cmd)


def add_shared_subcommands() -> None:
    """Discover and register shared commands from the full dependency chain.

    Searches every package between ``pyrig`` and the calling package for a
    ``<package>.rig.cli.shared_subcommands`` module and registers all functions
    found there as Typer commands. These commands are available in every
    pyrig-based project and can adapt their behavior to the calling project
    at runtime.

    For example, a ``version`` command defined once in pyrig automatically
    reports the version of whichever project invokes it.

    Example:
        $ uv run pyrig version
        pyrig version 3.1.5

        $ uv run myproject version
        myproject version 1.2.3

    Note:
        Commands are registered in dependency order (pyrig first, calling
        package last). When two packages define a command with the same name,
        the last registration takes precedence.
    """
    package_name = package_name_from_argv()
    package = import_module(package_name)
    all_shared_subcommands_modules = discover_equivalent_modules_across_dependents(
        shared_subcommands,
        pyrig,
        until_package=package,
    )
    for shared_subcommands_module in all_shared_subcommands_modules:
        sub_cmds = all_functions_from_module(shared_subcommands_module)
        for sub_cmd in sub_cmds:
            app.command()(sub_cmd)
