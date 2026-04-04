"""GitHub repository protection and security configuration.

Configures secure repository settings and branch protection rulesets on GitHub,
implementing pyrig's opinionated security defaults.
"""

from pyrig.rig.configs.git.branch_protection import RepoProtectionConfigFile


def protect_repository() -> None:
    """Apply security protections to the GitHub repository.

    Configures repository-level settings and branch protection rulesets.
    """
    RepoProtectionConfigFile.I.protect_repo()
