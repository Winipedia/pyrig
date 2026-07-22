"""Project-structure reconciliation for the `sync` CLI command."""

from collections.abc import Iterable
from pathlib import Path

import typer

from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def synchronize_project(files: Iterable[Path]) -> None:
    """Bring the project into its canonical state.

    Args:
        files: Specific files to synchronize. If empty, all files are synchronized.

    Run the ordered reconciliation steps that create missing package files,
    update managed configuration, and refresh generated tests. The operation
    is idempotent and safe to re-run.

    Raises:
        typer.Exit: With code 1 if any file was created or updated during
            the run.
    """
    files = tuple(files)
    changed_configs = ConfigFile.validate_concrete_subclasses()
    changed_tests = MirrorTestConfigFile.L.validate_concrete_subclasses()
    if changed_configs or changed_tests:
        raise typer.Exit(code=1)
