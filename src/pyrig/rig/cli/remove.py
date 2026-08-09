"""CLI command group for removing generated project artifacts."""

import typer

app = typer.Typer(no_args_is_help=True, help="Remove generated project artifacts.")


@app.command()
def pyc() -> None:
    """Remove all `__pycache__` directories from the project's source and test trees.

    Useful for clearing stale bytecode that may cause import errors or
    test-isolation issues after refactors, branch switches, or moving files
    around. Safe to run repeatedly.
    """
    from pyrig.rig.cli.commands.remove.pycache import remove_pycache  # noqa: PLC0415

    remove_pycache()
