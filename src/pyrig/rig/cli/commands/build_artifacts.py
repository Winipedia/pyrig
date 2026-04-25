"""Distributable artifact creation.

Entry point for the ``build`` CLI command, which triggers the build process
for all registered builders in the project.
"""

from pyrig.rig.builders.base.builder import BuilderConfigFile


def build_artifacts() -> None:
    """Build all distributable artifacts for the project.

    Discovers all concrete ``BuilderConfigFile`` subclasses, sorts them by
    priority, and runs the build lifecycle for each. Artifacts are written
    to the ``dist/`` directory with platform-specific names (e.g.,
    ``myapp-Linux``, ``myapp-Windows``, ``myapp-Darwin``). Builders whose
    output already exists in ``dist/`` are skipped.
    """
    BuilderConfigFile.validate_all_subclasses()
