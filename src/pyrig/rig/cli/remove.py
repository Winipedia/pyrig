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


@app.command()
def pyrig() -> None:
    """Remove pyrig and its footprint from the project entirely.

    Strips the `pyrig mk local` step from the health check workflow, removes
    the `pyrig sync` hook from the version control hook pipeline, and
    uninstalls pyrig and its plugins from the dev dependency group.

    Warning:
        One-way: everything pyrig previously generated is left in place as
        plain, standalone output, but pyrig itself is no longer wired into
        the project afterward.
    """
    from pyrig.rig.cli.commands.remove.pyrig import remove_pyrig  # noqa: PLC0415

    remove_pyrig()
