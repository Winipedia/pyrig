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

    Appends a minimal no-op function stub named after `name` to the project's
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
def subcls() -> None:
    """Scaffold a subclass of any pyrig class interactively.

    Launches a fuzzy-search prompt listing all ``DependencySubclass`` leaf
    subclasses found in pyrig and its dependents — both concrete classes
    (shown with their string representation) and abstract classes (shown by
    qualified name), sorted alphabetically by import path.

    After you select a class, pyrig creates the matching module file in your
    project (or validates it if it already exists), copies the source
    module's docstring into it, and appends a ready-to-edit subclass
    skeleton that imports and extends the class you chose.

    Example:
        $ uv run pyrig mk subcls
    """
    from pyrig.rig.cli.commands.make.subclass import make_subclass  # noqa: PLC0415

    make_subclass()


@app.command()
def local() -> None:
    """Create all version-control-ignored config files.

    Discovers every concrete config file subclass marked as version-control-ignored
    and validates each one: the file (and any missing parent directories) is
    created if absent, or updated to include any missing required configuration
    if already present.

    Examples:
        ```
        $ uv run pyrig mk local
        ```
    """
    from pyrig.rig.cli.commands.make.local import make_local_files  # noqa: PLC0415

    make_local_files()
