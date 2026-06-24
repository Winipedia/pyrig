"""Project-structure reconciliation run by the `sync` CLI command.

Provides the backend logic that brings a project into the exact state pyrig's
autouse conformance checks require, by running the three idempotent structural
fixups in their correct order.
"""

import typer

from pyrig.core.root import make_all_init_files
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def synchronize_project() -> None:
    """Run the three structural fixups in order to reconcile the project.

    Performs, in order:

        1. Create any missing `__init__.py` files so no package is an implicit
           namespace package.
        2. Create or update every managed `ConfigFile` across the project and
           its installed pyrig dependencies.
        3. Generate mirror test skeletons for all source modules, stubbing any
           untested function, class, or method.

    The order matters: inits first so every package is importable for the
    discovery the later steps rely on, then config files, then tests. Every
    step preserves existing user content and only adds what is missing or
    corrects what is wrong, so this function is idempotent and safe to re-run.

    Raises:
        typer.Exit: With code 1 if any file was created or updated, leaving
            this function usable as a git hook backend.
    """
    created_inits = make_all_init_files()
    changed_configs = ConfigFile.validate_concrete_subclasses()
    changed_tests = MirrorTestConfigFile.L.validate_concrete_subclasses()
    if created_inits or changed_configs or changed_tests:
        raise typer.Exit(code=1)
