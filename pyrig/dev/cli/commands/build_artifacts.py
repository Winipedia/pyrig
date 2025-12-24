"""Artifact build orchestration.

This module provides the main entry point for building all project
artifacts. It discovers all Builder subclasses and invokes each one.
"""

import logging

from pyrig.dev.builders.base.base import Builder

logger = logging.getLogger(__name__)


def build_artifacts() -> None:
    """Build all artifacts by invoking all registered Builder subclasses.

    Discovers all non-abstract Builder subclasses across all packages
    depending on pyrig and invokes each one to create its artifacts.
    """
    logger.info("Building all artifacts")
    Builder.init_all_non_abstract_subclasses()
    logger.info("Artifact build complete")
