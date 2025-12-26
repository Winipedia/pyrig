"""Development utilities requiring dev dependencies.

This package provides utility functions and decorators that depend on
development-time dependencies (packages in the `dev` dependency group).
These utilities are only available when pyrig is installed with dev dependencies.

The separation between `pyrig.src` and `pyrig.dev.utils` ensures that:

- Core functionality in `pyrig.src` has minimal runtime dependencies
- Development tools in `pyrig.dev.utils` can use heavier dependencies
- Production packages don't need to install dev dependencies

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
        'myproject'

    Parse version constraints and generate version ranges::

        >>> from pyrig.dev.utils.versions import VersionConstraint
        >>> vc = VersionConstraint(">=3.8,<3.12")
        >>> versions = vc.get_version_range(level="minor")
        >>> print(versions)
        [<Version('3.8')>, <Version('3.9')>, <Version('3.10')>, <Version('3.11')>]

    Create pytest fixtures with specific scopes::

        >>> from pyrig.dev.utils.testing import session_fixture
        >>> @session_fixture
        ... def database_connection():
        ...     return create_connection()

Note:
    These utilities are only available when pyrig is installed with dev
    dependencies. Attempting to import them in a runtime-only environment
    will raise an ImportError.
"""
