"""Project-structure reconciliation run by the ``sync`` CLI command.

Provides the backend logic that brings a project into the exact state pyrig's
autouse conformance checks require, by running the three idempotent structural
fixups in their correct order.
"""

from pyrig.core.root import make_all_init_files
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def synchronize_project() -> None:
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
    """
    make_all_init_files()
    ConfigFile.validate_all_subclasses()
    MirrorTestConfigFile.L.validate_all_subclasses()
