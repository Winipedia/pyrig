"""Discoverable Typer application builder for pyrig and pyrig-based projects.

Defines :class:`CLI`, a ``RigDependencySubclass`` that assembles the Typer
application and registers project-specific and shared commands discovered across
the package dependency chain. Dependent projects can subclass it to customize how
their command-line application is built without modifying pyrig.
"""

import logging
import sys
from itertools import chain
from pathlib import Path
from types import ModuleType

import typer

from pyrig.core.introspection.dependencies import (
    discover_equivalent_modules_across_dependents,
)
from pyrig.core.introspection.functions import module_functions
from pyrig.core.introspection.modules import (
    import_module_with_default,
    module_name_replacing_start_module,
)
from pyrig.core.strings import kebab_to_snake_case
from pyrig.rig.cli import cli, shared_subcommands, subcommands
from pyrig.rig.utils.dependency_subclass import RigDependencySubclass


class CLI(RigDependencySubclass):
    """Typer application builder with cross-package command discovery.

    Assembles the command-line application for pyrig and any pyrig-based project:
    creates the Typer app, attaches the verbosity callback, and registers both
    project-specific subcommands and shared subcommands discovered across the
    dependency chain.

    As a ``RigDependencySubclass``, a single leaf subclass is resolved at runtime
    (accessed via ``CLI.I``), so a dependent project may override any step of the
    build to customize its command-line application without modifying pyrig.
    """

    @classmethod
    def dependency_package(cls) -> ModuleType:
        """Return the package where ``CLI`` subclasses are defined.

        Scopes cross-package subclass discovery to the ``pyrig.rig.cli.cli``
        package so that only CLI implementations are found across dependent
        packages.

        Returns:
            The ``pyrig.rig.cli.cli`` package.
        """
        return cli

    def run(self) -> None:
        """Build the Typer application and invoke it.

        Constructs a fully configured app via ``app()`` and calls it, which parses
        ``sys.argv`` and dispatches the requested command. This is the behavior
        invoked by the console-script entry point through ``main()``.
        """
        self.app()()

    def app(self) -> typer.Typer:
        """Build a fully configured Typer application.

        Creates a base app and populates it with the verbosity callback and all
        discovered commands.

        Returns:
            A Typer app with the callback and every project-specific and shared
            command registered.
        """
        app = self.base_app()
        return self.build_app(app)

    def base_app(self) -> typer.Typer:
        """Create an empty base Typer application.

        Returns:
            A new Typer app configured to show help when invoked without
            arguments.
        """
        return typer.Typer(no_args_is_help=True)

    def build_app(self, app: typer.Typer) -> typer.Typer:
        """Register the callback and all commands onto the given app.

        Attaches the verbosity callback, then registers project-specific and
        shared subcommands in dependency order.

        Args:
            app: The Typer app to populate.

        Returns:
            The same app instance, now fully configured.
        """
        self.register_callback(app)
        self.register_subcommands(app)
        self.register_shared_subcommands(app)
        return app

    def register_callback(self, app: typer.Typer) -> None:
        """Attach the verbosity callback to the given app.

        Registers ``callback`` as the app's Typer callback so that the
        ``--verbose`` and ``--quiet`` options are parsed before any command runs.

        Args:
            app: The Typer app to attach the callback to.
        """
        app.callback()(self.callback)

    def callback(
        self,
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
        self.configure_logging(verbose, quiet)

    def configure_logging(self, verbose: int, quiet: int) -> None:
        """Configure logging based on verbosity and quietness levels.

        The logging level is determined by the difference between `verbose` and `quiet`
        counts, with `verbose` decreasing the level (more verbose) and `quiet`
        increasing it (less verbose). The log format also adapts to the verbosity level,
        showing more contextual information at higher verbosity.

        Args:
            verbose: The count of `--verbose` flags, increasing verbosity.
            quiet: The count of `--quiet` flags, decreasing verbosity.

        Note:
            Uses `logging.basicConfig` with `force=True` to ensure that the
            configuration is applied even if logging has already been configured
            by the calling project or other dependencies.
        """
        level = logging.INFO
        step = logging.INFO - logging.DEBUG
        level -= step * verbose
        level += step * quiet

        verbose_timestamps = 3
        verbose_modules = 2

        if verbose >= verbose_timestamps:
            fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        elif verbose == verbose_modules:
            fmt = "%(levelname)s [%(name)s] %(message)s"
        elif verbose == 1:
            fmt = "%(levelname)s: %(message)s"
        else:
            fmt = "%(message)s"

        logging.basicConfig(level=level, format=fmt, force=True)

    def register_subcommands(self, app: typer.Typer) -> None:
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
            subcommands, new_start_module_name=self.package_name()
        )
        subcommands_module = import_module_with_default(subcommands_module_name)

        if subcommands_module is None:
            return

        for cmd in module_functions(subcommands_module):
            app.command()(cmd)

    def register_shared_subcommands(self, app: typer.Typer) -> None:
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
        for shared_subcommands_module in chain(
            (shared_subcommands,),
            discover_equivalent_modules_across_dependents(
                shared_subcommands,
            ),
        ):
            sub_cmds = module_functions(shared_subcommands_module)
            for sub_cmd in sub_cmds:
                app.command()(sub_cmd)

    def package_name(self) -> str:
        """Return the package name of the invoking project.

        Derives the package name from the project name (the basename of
        ``sys.argv[0]``) by converting it from kebab-case to snake_case.

        For example, if the project is invoked as ``uv run my-project``, the
        package name would be ``my_project``.

        Returns:
            The package name of the invoking project, derived from the project name.
        """
        return self.package_name_from_project_name(self.project_name())

    def package_name_from_project_name(self, project_name: str) -> str:
        """Return the package name derived from the project name.

        Converts the project name from kebab-case to snake_case, so a
        project named ``my-project`` has the package name ``my_project``.

        Returns:
            Python-importable package name derived from the project name.
        """
        return kebab_to_snake_case(project_name)

    def project_name(self) -> str:
        """Extract the invoking project name from the command-line entry point.

        Reads ``sys.argv[0]`` and returns its basename. When a project is invoked
        through a registered console-script entry point (e.g. ``uv run my-project``),
        ``sys.argv[0]`` is the path to that entry point script, so its basename is
        the project name as it was registered.

        Returns:
            The basename of ``sys.argv[0]``, which is the project name as registered
            in the console-scripts entry point.

        Example:
            >>> # When invoked as: uv run my-project build
            >>> self.project_name()
            'my-project'
        """
        return Path(sys.argv[0]).name
