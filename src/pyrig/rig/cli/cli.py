"""CLI entry point and dynamic command registration for pyrig and pyrig-based projects.

Provides the main entry point with runtime command discovery from project-specific
and shared sources across the package dependency chain. Built on Typer.
"""

import logging

import typer

from pyrig.core.cli import package_name_from_argv
from pyrig.core.introspection.dependencies import (
    discover_equivalent_modules_across_dependents,
)
from pyrig.core.introspection.functions import module_functions
from pyrig.core.introspection.modules import (
    import_module_with_default,
    module_name_replacing_start_module,
)
from pyrig.rig.cli import shared_subcommands, subcommands

app = typer.Typer(no_args_is_help=True)


@app.callback()
def callback(
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        help="Increase verbosity: -v (DEBUG), -vv (modules), -vvv (timestamps)",
    ),
    quiet: int = typer.Option(
        0,
        "--quiet",
        "-q",
        count=True,
        help="Decrease verbosity: -q (WARNING), -qq (ERROR), -qqq (CRITICAL)",
    ),
) -> None:
    # cli is inherited by dependent projects, so the callback docstring is
    # intentionally left blank to avoid confusion in help messages
    """"""  # noqa: D419
    configure_logging(verbose, quiet)


def configure_logging(verbose: int, quiet: int) -> None:
    """Configure logging based on verbosity and quietness levels.

    The logging level is determined by the difference between `verbose` and `quiet`
    counts, with `verbose` decreasing the level (more verbose) and `quiet`
    increasing it (less verbose). The log format also adapts to the verbosity level,
    showing more contextual information at higher verbosity.

    Args:
        verbose: The count of `--verbose` flags, increasing verbosity.
        quiet: The count of `--quiet` flags, decreasing verbosity.

    Note:
        Uses `logging.basicConfig` with `force=True` to ensure
        that the configuration is applied even if logging has already been configured
        by the calling project or other dependencies.
    """
    level = logging.INFO
    step = logging.INFO - logging.DEBUG
    level -= step * verbose
    level += step * quiet

    if verbose >= 3:  # noqa: PLR2004
        fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    elif verbose == 2:  # noqa: PLR2004
        fmt = "%(levelname)s [%(name)s] %(message)s"
    elif verbose == 1:
        fmt = "%(levelname)s: %(message)s"
    else:
        fmt = "%(message)s"

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
    subcommands_module_name = module_name_replacing_start_module(
        subcommands, package_name_from_argv()
    )
    subcommands_module = import_module_with_default(subcommands_module_name)

    if subcommands_module is None:
        return

    for cmd in module_functions(subcommands_module):
        app.command()(cmd)


def add_shared_subcommands() -> None:
    """Discover and register shared commands from the full dependency chain.

    Searches pyrig itself and every package that depends on pyrig for a
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
        Commands are registered in dependency order (pyrig first, then all
        dependent packages in topological order). When two packages define a
        command with the same name, the last registration takes precedence.
    """
    for shared_subcommands_module in (
        shared_subcommands,
        *discover_equivalent_modules_across_dependents(
            shared_subcommands,
        ),
    ):
        sub_cmds = module_functions(shared_subcommands_module)
        for sub_cmd in sub_cmds:
            app.command()(sub_cmd)
