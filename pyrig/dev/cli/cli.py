"""CLI entry point and dynamic command registration system.

This module implements the main CLI entry point for pyrig and all pyrig-based
projects. It provides a dynamic command discovery and registration system that
automatically finds and registers commands from multiple sources across the
package dependency chain.

The CLI is built on Typer and uses pyrig's multi-package architecture to enable
extensibility. When a project depends on pyrig, it can define its own commands
that are automatically discovered and integrated into the CLI.

Command Discovery:
    The CLI discovers and registers commands from three sources:

    1. **Main entry point**: The `main()` function from `<package>.main` module
    2. **Project-specific commands**: All public functions from
       `<package>.dev.cli.subcommands` module
    3. **Shared commands**: All public functions from
       `<package>.dev.cli.shared_subcommands` modules across all packages in
       the dependency chain that depend on pyrig

    Discovery is performed by:
    - Extracting the package name from `sys.argv[0]`
    - Replacing module paths to find equivalent modules in the current package
    - Importing modules with file fallback for robustness
    - Extracting all public functions and registering them as Typer commands

Logging Configuration:
    The CLI provides flexible logging control through global options:
    - Default: INFO level with clean formatting (just messages)
    - `-q/--quiet`: WARNING level (errors and warnings only)
    - `-v`: DEBUG level with level prefix
    - `-vv`: DEBUG level with module names
    - `-vvv`: DEBUG level with timestamps and full details

Example:
    Running pyrig commands::

        $ uv run pyrig init
        $ uv run pyrig mkroot --priority
        $ uv run pyrig build
        $ uv run pyrig version

    Running with logging options::

        $ uv run pyrig -v mkroot  # Debug output
        $ uv run pyrig -vv build  # Debug with module names
        $ uv run pyrig -q init    # Quiet mode

    Running commands in a dependent project::

        $ uv run myproject deploy  # Custom command
        $ uv run myproject version # Shared command (shows myproject version)

See Also:
    add_subcommands: Project-specific command discovery
    add_shared_subcommands: Shared command discovery across packages
    configure_logging: Logging configuration callback
    main: CLI entry point function
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
"""The main Typer application instance for the CLI.

This is the root Typer app that all commands are registered to. It is configured
with `no_args_is_help=True` to automatically display help when the CLI is invoked
without any command.

Commands are registered to this app by `add_subcommands()` and
`add_shared_subcommands()` during CLI initialization.
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
    """Configure logging for the CLI based on verbosity flags.

    This is a Typer callback that runs before any command executes. It configures
    the Python logging system based on the verbosity flags provided by the user.

    The logging configuration affects all loggers in the application and provides
    different levels of detail:

    - **Default (no flags)**: INFO level, clean formatting (just messages)
    - **`-q/--quiet`**: WARNING level (only warnings and errors)
    - **`-v`**: DEBUG level with level prefix (e.g., "DEBUG: message")
    - **`-vv`**: DEBUG level with module names (e.g., "DEBUG [module.name] message")
    - **`-vvv+`**: DEBUG level with timestamps and full details

    Args:
        verbose: Verbosity level determined by the number of `-v` flags.
            0 = INFO (default), 1 = DEBUG, 2 = DEBUG with modules,
            3+ = DEBUG with timestamps. This is a count option, so each `-v`
            increments the value.
        quiet: If True, sets logging to WARNING level, showing only warnings
            and errors. Takes precedence over verbose flags.

    Note:
        The `force=True` parameter in `logging.basicConfig()` ensures that any
        existing logging configuration is overridden.
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

    Dynamically discovers and registers two types of commands for the current
    project:

    1. **Main entry point**: The `main()` function from `<package>.main`
    2. **Subcommands**: All public functions from `<package>.dev.cli.subcommands`

    The discovery process:
    1. Extracts the package name from `sys.argv[0]` (e.g., "pyrig" from
       "uv run pyrig")
    2. Replaces the root module name in pyrig's module paths with the current
       package name (e.g., `pyrig.main` → `myproject.main`)
    3. Converts module names to file paths and imports with file fallback
    4. Extracts all public functions from the subcommands module
    5. Registers each function as a Typer command on the global `app`

    This enables projects that depend on pyrig to define their own commands by
    creating a `<package>.dev.cli.subcommands` module with public functions.
    Each function becomes a CLI command automatically.

    Example:
        For a project "myproject" that depends on pyrig::

            # myproject/dev/cli/subcommands.py
            def deploy() -> None:
                '''Deploy the application.'''
                ...

            # Command line
            $ uv run myproject deploy

    Note:
        - The package name is extracted from `sys.argv[0]`, not from the current
          working directory
        - Functions are registered in the order they are defined in the module
        - Only public functions (not starting with `_`) are registered
        - The main() function is registered separately from subcommands

    See Also:
        pyrig.src.cli.get_pkg_name_from_argv: Package name extraction
        pyrig.src.modules.module.get_module_name_replacing_start_module: Module path transformation
        pyrig.src.modules.function.get_all_functions_from_module: Function extraction
    """  # noqa: E501
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

    Discovers and registers shared commands that are available across all
    pyrig-based projects. These commands are defined in
    `<package>.dev.cli.shared_subcommands` modules and are automatically
    available in all projects that depend on the package.

    The discovery process:
    1. Extracts the current package name from `sys.argv[0]`
    2. Imports the current package
    3. Finds all packages in the dependency chain from pyrig to the current
       package (e.g., [pyrig, intermediate_pkg, current_pkg])
    4. For each package, looks for a `dev.cli.shared_subcommands` module
    5. Extracts all public functions from each shared_subcommands module
    6. Registers each function as a Typer command on the global `app`

    This enables creating commands that work consistently across an ecosystem
    of related packages while adapting to each project's context. For example,
    the `version` command is defined in pyrig's shared_subcommands and is
    automatically available in all dependent projects, displaying the version
    of the project being run.

    Example:
        The `version` command defined in pyrig::

            # pyrig/dev/cli/shared_subcommands.py
            def version() -> None:
                '''Display the project version.'''
                project_name = get_project_name_from_argv()
                typer.echo(f"{project_name} version {get_version(project_name)}")

            # Command line
            $ uv run pyrig version
            pyrig version 3.1.5

            $ uv run myproject version
            myproject version 1.2.3

    Note:
        - Commands are registered in dependency order (pyrig first, then
          dependent packages)
        - If multiple packages define the same command name, the last one
          registered (from the most dependent package) takes precedence
        - The `until_pkg` parameter stops discovery at the current package,
          preventing discovery of packages that depend on the current package

    See Also:
        pyrig.src.modules.package.get_same_modules_from_deps_depen_on_dep: Module discovery
        pyrig.src.cli.get_pkg_name_from_argv: Package name extraction
        pyrig.dev.cli.shared_subcommands: Pyrig's shared commands
    """  # noqa: E501
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
    """Main entry point for the pyrig CLI.

    This is the primary entry point function that is called when the CLI is
    invoked (e.g., `uv run pyrig <command>`). It orchestrates the complete
    command discovery and registration process before invoking the Typer
    application.

    The function performs three steps:
    1. Discovers and registers project-specific commands via `add_subcommands()`
    2. Discovers and registers shared commands via `add_shared_subcommands()`
    3. Invokes the Typer app to parse arguments and execute the requested command

    This function is registered as a console script entry point in pyproject.toml,
    making it the executable target for the CLI.

    Example:
        When a user runs::

            $ uv run pyrig mkroot

        This function:
        1. Discovers pyrig's main() and subcommands (mkroot, init, build, etc.)
        2. Discovers shared commands (version, etc.)
        3. Invokes Typer, which parses "mkroot" and executes the mkroot command

    Note:
        - This function is called automatically by the console script entry point
        - It does not take any arguments; all CLI arguments are parsed by Typer
        - Logging configuration is handled by the `configure_logging` callback
          before any command executes

    See Also:
        add_subcommands: Project-specific command registration
        add_shared_subcommands: Shared command registration
        app: The Typer application instance
    """
    add_subcommands()
    add_shared_subcommands()
    app()
