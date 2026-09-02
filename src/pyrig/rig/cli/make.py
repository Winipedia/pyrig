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
def subcls(
    reference: Annotated[
        tuple[str, str] | None,
        typer.Argument(
            help="""Dotted module path and name of the class to subclass.
For example: pyrig.rig.tools.pyrigger Pyrigger""",
        ),
    ] = None,
) -> None:
    """Scaffold a subclass of an extensible pyrig class.

    Args:
        reference: A `(module_name, class_name)` pair identifying the class to
            subclass. If omitted, prompts the user to choose one interactively.

    Examples:
        ```
        $ uv run pyrig mk subcls
        $ uv run pyrig mk subcls pyrig.rig.tools.pyrigger Pyrigger
        ```
    """
    from pyrig.rig.cli.commands.make.subclass import make_subclass  # noqa: PLC0415

    make_subclass(reference)
