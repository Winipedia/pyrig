"""Artifact build orchestration.

Provides the entry point for building all project artifacts by discovering
and invoking all BuilderConfigFile subclasses.
"""

from pyrig.rig.builders.base.base import BuilderConfigFile


def build_artifacts() -> None:
    """Build all project artifacts.

    Discovers and validates all non-abstract BuilderConfigFile subclasses to
    create distributable artifacts.
    """
    BuilderConfigFile.validate_all_subclasses()
