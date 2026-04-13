"""GitHub repository protection and security configuration.

Configures secure repository settings and branch protection rulesets on GitHub,
implementing pyrig's opinionated security defaults.
"""

from pyrig.rig.configs.remote_version_control.branch_protection import (
    BranchProtectionConfigFile,
)


def protect_repository() -> None:
    """Apply security protections to the GitHub repository.

    Configures repository-level settings and branch protection rulesets.
    """
    BranchProtectionConfigFile.I.protect_repo()
