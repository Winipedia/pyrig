"""Artifact build orchestration.

Provides the entry point for building all project artifacts by discovering
and invoking all Builder subclasses.
"""

import logging

from pyrig.dev.builders.base.base import Builder

logger = logging.getLogger(__name__)


def build_artifacts() -> None:
    """Build all project artifacts.

    Discovers and invokes all non-abstract Builder subclasses to create
    distributable artifacts.
    """
    logger.info("Building all artifacts")
    Builder.init_all_non_abstract_subclasses()
    logger.info("Artifact build complete")
