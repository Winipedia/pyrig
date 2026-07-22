"""CLI command group for scaffolding new project artifacts."""

import typer

app = typer.Typer(no_args_is_help=True, help="Scaffold new project artifacts.")


@app.command()
def cmd(
    name: str = typer.Argument(help="Name of the command to create."),
    *,
    shared: bool = typer.Option(
        default=False,
        help="Whether the command should be shared in subsequent projects.",
    ),
) -> None:
    """Scaffold a new CLI subcommand stub.

    Adds a no-op function stub named after `name` to the project's
    subcommand module, or the shared subcommand module when `shared` is `True`.
    The target module is created if it does not already exist. Kebab-case names
    are normalized to snake_case for the generated function name.

    Args:
        name: Name of the subcommand to create. Accepts kebab-case or snake_case.
        shared: When `True`, the stub is added to the shared subcommand module,
            making it available to every dependent project rather than only this one.

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
    """Create all missing `__init__.py` files in the project.

    Echoes each directory where a file was created to standard output.

    Returns:
        Directories where `__init__.py` files were created. Empty if all
        already existed.
    """
    from pyrig.rig.cli.commands.make.inits import (  # noqa: PLC0415
        make_project_init_files,
    )

    make_project_init_files()


@app.command()
def local() -> None:
    """Create or update all version-control-ignored config files.

    For each version-control-ignored config file, creates the file (and any
    missing parent directories) if absent, or updates it to include any
    missing required configuration if already present.
    """
    from pyrig.rig.cli.commands.make.local import make_local_files  # noqa: PLC0415

    make_local_files()


@app.command()
def subcls() -> None:
    """Scaffold a subclass of any pyrig class interactively.

    Prompts the user to select a class, then appends a subclass skeleton to
    the matching module file in the project, creating it first if it does not
    exist. The skeleton imports and extends the chosen class.
    """
    from pyrig.rig.cli.commands.make.subclass import make_subclass  # noqa: PLC0415

    make_subclass()
