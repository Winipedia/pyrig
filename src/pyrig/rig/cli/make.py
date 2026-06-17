"""The ``mk`` command group for scaffolding new project artifacts.

Defines the group's Typer ``app`` and its sub-commands (``pyrig mk subcls``,
``pyrig mk cmd``, ``pyrig mk fixture``). ``subcommands`` binds this ``app`` to
the name ``mk`` so the CLI discovery registers it as the ``mk`` command group;
importing this module also registers the sub-commands defined below.
"""

import typer

app = typer.Typer(no_args_is_help=True, help="Scaffold new project artifacts.")


@app.command()
def subcls() -> None:
    """Scaffold a subclass of any pyrig class interactively.

    Launches a fuzzy-search prompt listing all `DependencySubclass` leaf subclasses
    found in pyrig and its dependents — both concrete classes (shown with their string
    representation) and abstract classes (shown by qualified name), sorted
    alphabetically by import path.

    After you select a class, pyrig creates the matching module file in your
    project (or validates it if it already exists), copies the source module's
    docstring into it, and appends a ready-to-edit subclass skeleton that
    imports and extends the class you chose.

    Example:
        $ uv run pyrig mk subcls
    """
    from pyrig.rig.cli.commands.make_subclass import make_subclass  # noqa: PLC0415

    make_subclass()


@app.command()
def cmd(
    name: str = typer.Argument(help="Name of the command to create."),
    *,
    shared: bool = typer.Option(
        default=False,
        help="Whether the command should be shared in subsequent projects.",
    ),
) -> None:
    """Create a new CLI subcommand stub for this project.

    Appends a minimal function stub to `rig/cli/subcommands.py` or
    `rig/cli/shared_subcommands.py` depending on the ``shared`` flag.
    The target module is created automatically if it does not yet exist.
    Kebab-case names are normalized to snake_case for the generated function name.

    Args:
        name: Name of the subcommand to create. Accepts kebab-case or snake_case.
        shared: If `True`, the stub is added to `rig/cli/shared_subcommands.py` instead,
            making it accessible to every pyrig-based project in the ecosystem.

    Examples:
        $ uv run pyrig mk cmd my-command
        $ uv run pyrig mk cmd my-command --shared
    """
    from pyrig.rig.cli.commands.make_subcommand import make_subcommand  # noqa: PLC0415

    make_subcommand(name, shared=shared)


@app.command()
def fixture(
    name: str = typer.Argument(help="Name of the fixture to create."),
) -> None:
    """Scaffold a new pytest fixture stub in the project's shared fixtures module.

    Appends an `@pytest.fixture`-decorated function stub to the shared fixtures
    module. The file is created if it does not already exist. If `import pytest`
    is not already present in the module, it is inserted automatically.

    The name is normalized from kebab-case to snake_case so it forms a valid
    Python identifier (e.g. `my-new-fixture` becomes `my_new_fixture`).

    Example:
        $ uv run pyrig mk fixture my-fixture
    """
    from pyrig.rig.cli.commands.make_fixture import make_fixture  # noqa: PLC0415

    make_fixture(name)
