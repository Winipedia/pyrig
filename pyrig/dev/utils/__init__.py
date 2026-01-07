"""Development utilities requiring dev dependencies.

Utility functions and decorators that depend on development-time dependencies.
These are only available when pyrig is installed with dev dependencies, ensuring
production packages don't carry unnecessary dependencies.

Modules:
    github_api: GitHub API utilities and repository ruleset management
    packages: Package discovery utilities
    resources: Resource fallback decorators for network operations
    testing: Pytest fixture decorators and test utilities
    urls: URL construction utilities for GitHub, PyPI, Codecov
    version_control: Git utilities for repository configuration
    versions: Version constraint parsing and range generation

Examples:
    Discover packages with depth limit::

        >>> from pyrig.dev.utils.packages import find_packages
        >>> find_packages(depth=0)
        ['myproject', 'tests']

    Parse version constraints::

        >>> from pyrig.dev.utils.versions import VersionConstraint
        >>> vc = VersionConstraint(">=3.8,<3.12")
        >>> vc.get_version_range(level="minor")
        [<Version('3.8')>, <Version('3.9')>, <Version('3.10')>, <Version('3.11')>]

Note:
    Requires pyrig installation with dev dependencies. Importing in a runtime-only
    environment will raise ImportError.
"""
