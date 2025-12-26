"""Development utilities requiring dev dependencies.

This package contains utility functions and decorators that depend on
development-time dependencies (packages in the `dev` dependency group).
These utilities are only available when pyrig-dev is installed.

The separation between `pyrig.src` and `pyrig.dev.utils` ensures that:
- Core functionality in `pyrig.src` has minimal dependencies
- Development tools in `pyrig.dev.utils` can use heavier dependencies
- Runtime packages don't need to install dev dependencies

Modules:
    - `packages`: Package discovery and source package identification
    - `resources`: Resource fallback decorators for network operations
    - `testing`: Pytest fixture decorators and test utilities
    - `versions`: Version constraint parsing and range generation
    - `github`: GitHub API utilities for repository management

Example:
    >>> from pyrig.dev.utils.packages import get_src_package
    >>> from pyrig.dev.utils.versions import VersionConstraint
    >>>
    >>> pkg = get_src_package()
    >>> vc = VersionConstraint(">=3.8,<3.12")
    >>> versions = vc.get_version_range(level="minor")

Note:
    These utilities are only available when `pyrig-dev` is installed. If you
    try to import them in a runtime-only environment, you'll get an ImportError.
"""
