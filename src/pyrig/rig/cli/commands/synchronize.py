"""Project-structure reconciliation for the `sync` CLI command."""

import typer

from pyrig.core.root import make_all_init_files
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def synchronize_project() -> None:
    """Reconcile the project's structure by running three ordered fixups.

    Performs, in order:

        1. Create any missing `__init__.py` files so no package is an implicit
           namespace package.
        2. Create or update every managed config file across the project and
           its installed pyrig dependencies.
        3. Generate mirror test skeletons for all source modules, stubbing any
           untested function, class, or method.

    The order matters: init files first so every package is importable for the
    discovery the later steps rely on, then config files, then tests. Every
    step preserves existing user content and only adds what is missing or
    corrects what is wrong, making this function safe to re-run.

    Raises:
        typer.Exit: With code 1 if any file was created or updated during the
            run; exits with code 0 if everything was already correct.
    """
    created_inits = make_all_init_files()
    changed_configs = ConfigFile.validate_concrete_subclasses()
    changed_tests = MirrorTestConfigFile.L.validate_concrete_subclasses()
    if created_inits or changed_configs or changed_tests:
        raise typer.Exit(code=1)
