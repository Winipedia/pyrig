"""Artifact build orchestration.

Provides the entry point for building all project artifacts by discovering
and invoking all BuilderConfigFile subclasses.
"""

import logging

from pyrig.dev.builders.base.base import BuilderConfigFile

logger = logging.getLogger(__name__)


def build_artifacts() -> None:
    """Build all project artifacts.

    Discovers and invokes all non-abstract BuilderConfigFile subclasses to create
    distributable artifacts.
    """
    logger.info("Building all artifacts")
    BuilderConfigFile.init_all_subclasses()
    logger.info("Artifact build complete")
