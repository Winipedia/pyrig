"""CLI entry point and dynamic command registration for pyrig and pyrig-based projects.

Provides the main entry point with runtime command discovery from project-specific
and shared sources across the package dependency chain. Built on Typer.
"""

from pyrig.rig.cli.cli.cli import CLI


def main() -> None:
    """Run the CLI application.

    Registers all project-specific and shared commands, then invokes the Typer
    app to parse arguments and dispatch the requested command. Called automatically
    by the console script entry point defined in `pyproject.toml`.
    """
    CLI.I.run()
