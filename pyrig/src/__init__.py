"""Runtime utilities and source code infrastructure for pyrig.

This package provides production-ready utilities and helper functions that can be
used both by pyrig itself and by projects that depend on pyrig. Unlike `pyrig.dev`,
which contains development-only tools, the utilities in `pyrig.src` are designed
for runtime use and have minimal dependencies.

The package includes utilities for:
    - **Python introspection**: Module discovery, class inspection, function
      extraction, and package traversal
    - **CLI support**: Command-line argument parsing and project name extraction
    - **Git operations**: Repository URL parsing, GitHub integration, and
      authentication token management
    - **Graph structures**: Directed graph implementation for dependency analysis
    - **String manipulation**: Naming convention transformations (snake_case,
      PascalCase, kebab-case)
    - **Resource access**: PyInstaller-compatible resource file loading
    - **Testing utilities**: Test generation conventions and assertion helpers
    - **Data structures**: Nested structure comparison and validation
    - **OS utilities**: Subprocess execution with enhanced error handling

Modules:
    cli: CLI utilities for extracting project and package names from command-line
        arguments.
    consts: Constants used across pyrig modules, including standard development
        dependencies.
    git: GitHub repository utilities for token management, URL parsing, and
        GitHub Actions detection.
    graph: Directed graph implementation for analyzing package dependency
        relationships.
    iterate: Utilities for iterating over and comparing nested data structures.
    resource: Resource file access utilities that work in both development and
        PyInstaller-bundled environments.
    string: String manipulation and naming convention transformation utilities.

Subpackages:
    management: Project initialization and management utilities for creating
        project structure, managing dependencies, and versioning.
    modules: Python module and package introspection utilities for module
        discovery, class inspection, function extraction, and package traversal.
    os: Operating system utilities for subprocess execution and command discovery.
    testing: Testing utilities and test generation infrastructure including
        automatic test skeleton generation and assertion helpers.

Usage:
    Import specific utilities as needed in your runtime code::

        >>> from pyrig.src.modules.package import get_pkg_name_from_cwd
        >>> from pyrig.src.git import get_repo_url_from_git
        >>> from pyrig.src.string import make_name_from_obj

    These utilities are safe to use in production code and have minimal
    dependencies compared to the development tools in `pyrig.dev`.

Note:
    This package is intended for runtime use and can be imported in production
    code. For development-only tools (configuration generators, builders, etc.),
    see `pyrig.dev`.

See Also:
    pyrig.dev: Development tools and configuration generators
    pyrig.resources: Static resource files used by development tools
"""
