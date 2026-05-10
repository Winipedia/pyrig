"""Distributable artifact creation.

Entry point for the ``build`` CLI command, which triggers the build process
for all registered builders in the project.
"""

from pyrig.rig.builders.base.builder import BuilderConfigFile


def build_artifacts() -> None:
    """Build all distributable artifacts for the project.

    Validates all concrete ``BuilderConfigFile`` subclasses.
    """
    BuilderConfigFile.validate_all_subclasses()
