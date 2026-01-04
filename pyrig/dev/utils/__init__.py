"""Development utilities requiring dev dependencies.

Utility functions and decorators that depend on development-time dependencies.
These are only available when pyrig is installed with dev dependencies, ensuring
production packages don't carry unnecessary dependencies.

Modules:
    git: GitHub API utilities and repository ruleset management
    packages: Package discovery and source package identification
    resources: Resource fallback decorators for network operations
    testing: Pytest fixture decorators and test utilities
    versions: Version constraint parsing and range generation

Examples:
    Discover the main source package::

        >>> from pyrig.dev.utils.packages import get_src_package
        >>> pkg = get_src_package()
        >>> print(pkg.__name__)
        myproject

    Parse version constraints::

        >>> from pyrig.dev.utils.versions import VersionConstraint
        >>> vc = VersionConstraint(">=3.8,<3.12")
        >>> vc.get_version_range(level="minor")
        [<Version('3.8')>, <Version('3.9')>, <Version('3.10')>, <Version('3.11')>]

Note:
    Requires pyrig installation with dev dependencies. Importing in a runtime-only
    environment will raise ImportError.
"""
