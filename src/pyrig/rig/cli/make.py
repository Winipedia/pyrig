"""CLI command group for scaffolding new project artifacts."""

from typing import Annotated

import typer

app = typer.Typer(no_args_is_help=True, help="Scaffold new project artifacts.")


@app.command()
def cmd(
    name: Annotated[str, typer.Argument(help="Name of the command to create.")],
    *,
    shared: Annotated[
        bool,
        typer.Option(
            help="Whether the command should be shared in subsequent projects.",
        ),
    ] = False,
) -> None:
    """Scaffold a new CLI subcommand stub.

    Args:
        name: Name of the subcommand to create. Accepts kebab-case or snake_case.
        shared: When `True`, scaffolds the stub in the module shared across every
            project that depends on this one, instead of this project's own
            subcommand module.

    Examples:
        ```
        $ uv run pyrig mk cmd my-command
        $ uv run pyrig mk cmd my-command --shared
        ```
    """
    from pyrig.rig.cli.commands.make.subcommand import (  # noqa: PLC0415
        make_subcommand,
    )

    make_subcommand(name, shared=shared)


@app.command()
def inits() -> None:
    """Create all missing `__init__.py` files in the project."""
    from pyrig.rig.cli.commands.make.inits import (  # noqa: PLC0415
        make_project_init_files,
    )

    make_project_init_files()


@app.command()
def local() -> None:
    """Create or update all version-control-ignored config files."""
    from pyrig.rig.cli.commands.make.local import make_local_files  # noqa: PLC0415

    make_local_files()


@app.command()
def subcls() -> None:
    """Scaffold a subclass of any pyrig class interactively."""
    from pyrig.rig.cli.commands.make.subclass import make_subclass  # noqa: PLC0415

    make_subclass()
