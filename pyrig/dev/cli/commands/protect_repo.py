"""GitHub repository protection and security configuration.

Configures secure repository settings and branch protection rulesets on GitHub,
implementing pyrig's opinionated security defaults.
"""

import logging

from pyrig.dev.configs.git.branch_protection import RepoProtectionConfigFile

logger = logging.getLogger(__name__)


def protect_repository() -> None:
    """Apply security protections to the GitHub repository.

    Configures repository-level settings and branch protection rulesets.
    """
    logger.info("Protecting repository")
    RepoProtectionConfigFile.L.protect_repo()
    logger.info("Repository protection complete")
