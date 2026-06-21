"""Project-structure reconciliation run by the ``sync`` CLI command.

Provides the backend logic that brings a project into the exact state pyrig's
autouse conformance checks require, by running the three idempotent structural
fixups in their correct order.
"""

from pyrig.core.root import make_all_init_files
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def synchronize_project() -> bool:
    """Run the three structural fixups in order to reconcile the project.

    Executes, in order:

        1. ``make_init_files()`` — create any missing ``__init__.py`` files
           (satisfies the ``no_namespace_packages`` check).
        2. ``ConfigFile.validate_all_subclasses()`` — create or update every
           managed ``ConfigFile`` (satisfies the ``all_config_files_correct``
           check).
        3. ``MirrorTestConfigFile.L.validate_all_subclasses()`` — generate
           mirror test skeletons for all source modules (satisfies the
           ``all_modules_tested`` check).

    The order matters: inits first so every package is importable for the
    discovery the later steps rely on, then config files, then tests. Every
    step preserves existing user content and only adds what is missing or
    corrects what is wrong, so this function is idempotent and safe to re-run.

    Returns:
        ``True`` if the project was already fully in sync; ``False`` if any
        file was created or updated. A ``False`` result causes the ``sync``
        CLI command to exit with code 1, making it usable as a git hook.
    """
    return not (
        make_all_init_files()
        or ConfigFile.validate_all_subclasses()
        or MirrorTestConfigFile.L.validate_all_subclasses()
    )
