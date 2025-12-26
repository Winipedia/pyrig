"""Python module and package introspection utilities.

This package provides comprehensive utilities for working with Python's module
system, including module discovery, class introspection, function extraction,
and package traversal. These tools power pyrig's automatic discovery of
ConfigFile subclasses, Builder implementations, and test fixtures across
multiple packages in a dependency chain.

The package enables pyrig's multi-package architecture where dependent packages
can extend pyrig's functionality by defining their own ConfigFile subclasses,
Builder implementations, and CLI commands that are automatically discovered
and integrated.

Modules:
    - **class_**: Class introspection utilities including method extraction,
      subclass discovery with intelligent parent class filtering, and cached
      instance management
    - **function**: Function detection and extraction utilities for identifying
      callable objects in modules and filtering by naming conventions
    - **imports**: Import utilities for dynamically importing modules and
      packages with fallback mechanisms
    - **inspection**: Low-level inspection utilities for unwrapping decorators,
      accessing object metadata, and analyzing function signatures
    - **module**: Module loading, path conversion, and cross-package module
      discovery utilities for finding equivalent modules across dependencies
    - **package**: Package discovery, traversal, dependency graph analysis,
      and project name conversions
    - **path**: Path utilities for converting between module names and file
      paths, handling frozen environments (PyInstaller)

The utilities support both static analysis (without importing) and dynamic
introspection (with importing), making them suitable for code generation,
testing frameworks, and package management tools.

Example:
    >>> from pyrig.src.modules.package import DependencyGraph
    >>> from pyrig.src.modules.class_ import get_all_nonabstract_subclasses
    >>> from pyrig.dev.configs.base.base import ConfigFile
    >>>
    >>> # Discover all ConfigFile subclasses across dependent packages
    >>> subclasses = get_all_nonabstract_subclasses(ConfigFile)
    >>> [cls.__name__ for cls in subclasses]
    ['PyprojectConfigFile', 'GitignoreConfigFile', ...]

See Also:
    pyrig.dev.configs: Uses class_ for ConfigFile discovery
    pyrig.dev.builders: Uses class_ for Builder discovery
    pyrig.dev.cli: Uses function and module for command discovery
"""
