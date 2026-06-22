"""The ``mk`` command group for scaffolding new project artifacts.

Defines the group's Typer ``app`` and its sub-commands (``pyrig mk subcls``,
``pyrig mk cmd``, ``pyrig mk fixture``). ``subcommands`` binds this ``app`` to
the name ``mk`` so the CLI discovery registers it as the ``mk`` command group;
importing this module also registers the sub-commands defined below.
"""

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
    from pyrig.rig.cli.commands.make.subcommand import (  # noqa: PLC0415
        make_subcommand,
    )

    make_subcommand(name, shared=shared)


@app.command()
def local() -> None:
    """Create all version-control-ignored config files for local development.

    Discovers every ``ConfigFile`` subclass whose ``version_control_ignored()``
    returns ``True`` and creates the file on disk if it does not already exist.
    Parent directories are created automatically.

    Useful as a CI/CD setup step: gitignored files (such as ``.env`` or
    ``.scratch.py``) are never committed, so they must be created in the CI
    environment before running hooks or checks that expect them to be present.

    Examples:
        $ uv run pyrig mk local
    """
    from pyrig.rig.cli.commands.make.local import make_local_files  # noqa: PLC0415

    make_local_files()
