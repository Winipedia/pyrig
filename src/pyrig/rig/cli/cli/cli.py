"""Typer app assembly with cross-package command discovery for pyrig-based projects."""

import logging
import sys
from itertools import chain
from pathlib import Path
from types import ModuleType

import typer

from pyrig.core.dependency_subclass import DependencySubclass
from pyrig.core.introspection.dependencies import (
    discover_equivalent_modules_across_dependents,
)
from pyrig.core.introspection.functions import module_functions
from pyrig.core.introspection.modules import (
    import_module_with_default,
    module_name_replacing_start_module,
)
from pyrig.core.strings import kebab_to_snake_case, snake_to_kebab_case
from pyrig.rig.cli import cli, shared_subcommands, subcommands


class CLI(DependencySubclass):
    """Typer application builder with cross-package command discovery.

    Assembles the command-line application for pyrig and any pyrig-based project:
    creates the Typer app, attaches the verbosity callback, and registers both
    project-specific subcommands and shared subcommands discovered across the
    dependency chain.

    A single leaf subclass is resolved at runtime (accessed via `CLI.I`), so a
    dependent project may subclass `CLI` to override any step of the build without
    modifying pyrig.
    """

    @classmethod
    def dependency_package(cls) -> ModuleType:
        """Return the `pyrig.rig.cli.cli` package.

        Returns:
            The `pyrig.rig.cli.cli` package module.
        """
        return cli

    def run(self) -> None:
        """Build the Typer application and invoke it.

        Constructs a fully configured app and calls it, which parses `sys.argv`
        and dispatches the requested command. This is the entry point invoked by
        the console-script.
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

        Registers `self.callback` as the app's Typer callback so that the
        `--verbose` and `--quiet` options are parsed before any command runs.

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

        Derives the calling package from `sys.argv[0]`, constructs the module
        name `<package>.rig.cli.subcommands`, and registers every function
        defined in that module as a Typer command. Module-level `typer.Typer`
        instances in that module are registered as command groups named after
        their variable (e.g. an `mk` group exposing `pyrig mk <command>`); their
        sub-commands are defined in their own module and imported only for the
        group object, so they are not picked up as top-level commands.

        This allows any pyrig-based project to define its own CLI commands simply
        by adding functions to `<package>.rig.cli.subcommands`.

        Args:
            app: The Typer app to register the commands onto.

        Note:
            Only functions defined directly in the subcommands module are
            registered; imported functions are excluded. If the module cannot be
            imported, registration is silently skipped.
        """
        subcommands_module_name = module_name_replacing_start_module(
            subcommands, new_start_module_name=self.package_name()
        )
        subcommands_module = import_module_with_default(subcommands_module_name)

        if subcommands_module is None:
            return

        self.register_direct_subcommands(app=app, module=subcommands_module)
        self.register_subcommand_groups(app=app, module=subcommands_module)

    def register_shared_subcommands(self, app: typer.Typer) -> None:
        """Discover and register shared commands from the full dependency chain.

        Searches pyrig itself and every package that depends on pyrig for a
        `<package>.rig.cli.shared_subcommands` module and registers both its
        top-level command functions and its `typer.Typer` command groups. These
        commands are available in every pyrig-based project and can adapt their
        behavior to the calling project at runtime.

        For example, a `version` command defined once in pyrig automatically
        reports the version of whichever project invokes it.

        Args:
            app: The Typer app to register the commands onto.

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
            self.register_direct_subcommands(app=app, module=shared_subcommands_module)
            self.register_subcommand_groups(app=app, module=shared_subcommands_module)

    def register_direct_subcommands(self, app: typer.Typer, module: ModuleType) -> None:
        """Register every function defined in a module as a top-level command.

        Adds each function found directly in `module` to `app` as a flat Typer
        command. Imported functions are excluded; module-level `typer.Typer` group
        instances are registered separately by `register_subcommand_groups`.

        Args:
            app: The Typer app to register the commands onto.
            module: The subcommands module to scan for command functions.
        """
        for func in module_functions(module):
            app.command()(func)

    def register_subcommand_groups(self, app: typer.Typer, module: ModuleType) -> None:
        """Register every `typer.Typer` instance in a module as a named command group.

        Attaches each `typer.Typer` found in the module's namespace to `app`
        under its attribute name (e.g. an `mk` variable becomes the `mk` command
        group, exposing `pyrig mk <command>`).

        Args:
            app: The Typer app to register the command groups onto.
            module: The subcommands module to scan for group instances.
        """
        for name, group in self.module_subcommand_groups(module).items():
            app.add_typer(group, name=name)

    def module_subcommand_groups(self, module: ModuleType) -> dict[str, typer.Typer]:
        """Return the Typer command groups defined in a subcommands module.

        Scans the module's namespace for `typer.Typer` instances and maps each
        to the attribute name it is bound to. Imported instances are included
        as long as they are bound to a module-level name.

        Args:
            module: The subcommands module to scan.

        Returns:
            Mapping of attribute name to the `typer.Typer` group bound to it.
        """
        return {
            snake_to_kebab_case(name): obj
            for name, obj in vars(module).items()
            if isinstance(obj, typer.Typer)
        }

    def package_name(self) -> str:
        """Return the snake_case package name of the invoking project.

        Derives the package name from the project name (the basename of
        `sys.argv[0]`) by converting it from kebab-case to snake_case.
        For example, if the project is invoked as `uv run my-project`, the
        package name is `my_project`.

        Returns:
            Python-importable package name of the invoking project.
        """
        return self.project_name_as_package_name(self.project_name())

    def project_name_as_package_name(self, project_name: str) -> str:
        """Return the Python-importable package name derived from the project name.

        Converts `project_name` from kebab-case to snake_case, so a project
        named `my-project` has the package name `my_project`.

        Args:
            project_name: Kebab-case project name to convert.

        Returns:
            Python-importable package name derived from `project_name`.
        """
        return kebab_to_snake_case(project_name)

    def project_name(self) -> str:
        """Return the basename of `sys.argv[0]` as the invoking project name.

        When a project is invoked through a registered console-script entry point
        (e.g. `uv run my-project`), `sys.argv[0]` is the path to that script, so
        its basename is the project name as it was registered.

        Returns:
            The basename of `sys.argv[0]`.
        """
        return Path(sys.argv[0]).name
