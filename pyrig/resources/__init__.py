"""Static resource files for pyrig development tools.

This package contains static resource files used by pyrig's development tools
and configuration generators. These files serve as fallback templates when
creating new projects or when network operations fail.

The resources are accessed using pyrig's resource management system via
`pyrig.src.resource.get_resource_path()`, which provides unified access that
works in both development and PyInstaller-bundled executables.

Resource Files:
    GITIGNORE: GitHub's standard Python .gitignore template. Used as a fallback
        when fetching the latest .gitignore from GitHub fails, and as the default
        template for new projects created with `pyrig init`.

    LATEST_PYTHON_VERSION: Latest stable Python version number (e.g., "3.14.2").
        Used as a fallback when fetching the current Python version from
        endoflife.date API fails. Updated periodically in pyrig development mode.

    MIT_LICENSE_TEMPLATE: MIT License template text with placeholders for [year]
        and [fullname]. Used when generating LICENSE files for new projects.

Usage:
    Resources are accessed via the get_resource_path function::

        >>> from pyrig import resources
        >>> from pyrig.src.resource import get_resource_path
        >>>
        >>> # Get path to a resource file
        >>> gitignore_path = get_resource_path("GITIGNORE", resources)
        >>> content = gitignore_path.read_text()

    Resources are typically used with fallback decorators::

        >>> from pyrig.dev.utils.resources import (
        ...     return_resource_content_on_fetch_error
        ... )
        >>> import requests
        >>>
        >>> @return_resource_content_on_fetch_error(resource_name="GITIGNORE")
        ... def fetch_gitignore() -> str:
        ...     response = requests.get("https://api.github.com/gitignore/...")
        ...     response.raise_for_status()
        ...     return response.text

Note:
    These resources are development-time assets used by pyrig's configuration
    generators and CLI commands. They are not intended for direct use in
    production runtime code.

    When running in pyrig development mode (detected via src_pkg_is_pyrig()),
    successful network fetches automatically update these resource files to
    keep fallback content current.

    Projects created with pyrig will have their own `resources/` package for
    application-specific resource files. This package is specifically for
    pyrig's internal development tools.

See Also:
    pyrig.src.resource.get_resource_path: Function for accessing resource files
    pyrig.dev.utils.resources: Decorators for network fallback to resources
    pyrig.dev.configs.python.resources_init: Generator for project resources package
"""
