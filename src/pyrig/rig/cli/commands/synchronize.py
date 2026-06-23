"""Project-structure reconciliation run by the ``sync`` CLI command.

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

    Executes, in order:

        1. ``make_all_init_files()`` — create any missing ``__init__.py`` files
           (satisfies the ``no_namespace_packages`` check).
        2. ``ConfigFile.validate_concrete_subclasses()`` — create or update every
           managed ``ConfigFile`` (satisfies the ``all_config_files_correct``
           check).
        3. ``MirrorTestConfigFile.L.validate_concrete_subclasses()`` — generate
           mirror test skeletons for all source modules (satisfies the
           ``all_modules_tested`` check).

    The order matters: inits first so every package is importable for the
    discovery the later steps rely on, then config files, then tests. Every
    step preserves existing user content and only adds what is missing or
    corrects what is wrong, so this function is idempotent and safe to re-run.

    Raises:
        typer.Exit: With code 1 if any file was created or updated, making
            this function usable as a git hook backend.

    Note:
        All three calls are assigned to variables before the boolean
        combination so that every fixup always runs. Using ``or`` or ``and``
        directly on the call expressions would short-circuit and skip the
        remaining fixups the moment one returns a non-empty (or empty) tuple.
    """
    created_inits = make_all_init_files()
    changed_configs = ConfigFile.validate_concrete_subclasses()
    changed_tests = MirrorTestConfigFile.L.validate_concrete_subclasses()
    if created_inits or changed_configs or changed_tests:
        raise typer.Exit(code=1)
