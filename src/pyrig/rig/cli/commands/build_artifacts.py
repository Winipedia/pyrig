"""Distributable artifact creation.

Entry point for the ``build`` CLI command, which validates all registered
builders and triggers the build process for any whose artifact is missing.
"""

from pyrig.rig.builders.base.builder import BuilderConfigFile


def build_artifacts() -> None:
    """Validate and build missing distributable artifacts for the project.

    Validates all concrete ``BuilderConfigFile`` subclasses.
    """
    BuilderConfigFile.validate_all_subclasses()
