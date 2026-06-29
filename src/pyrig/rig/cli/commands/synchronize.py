"""Project-structure reconciliation for the `sync` CLI command."""

import typer

from pyrig.core.root import make_all_init_files
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def synchronize_project() -> None:
    """Bring the project into its canonical state.

    Run the ordered reconciliation steps that create missing package files,
    update managed configuration, and refresh generated tests. The operation
    is idempotent and safe to re-run.

    Raises:
        typer.Exit: With code 1 if any file was created or updated during
            the run.
    """
    created_inits = make_all_init_files()
    changed_configs = ConfigFile.validate_concrete_subclasses()
    changed_tests = MirrorTestConfigFile.L.validate_concrete_subclasses()
    if created_inits or changed_configs or changed_tests:
        raise typer.Exit(code=1)
