"""Python module and package introspection utilities.

This package provides comprehensive utilities for working with Python's module
system, including module discovery, class introspection, function extraction,
and package traversal. These tools power pyrig's automatic discovery of
ConfigFile subclasses, Builder implementations, and test fixtures.

Modules:
    class_: Class introspection utilities including method extraction and
        subclass discovery with intelligent parent class filtering.
    function: Function detection and extraction utilities for identifying
        callable objects in modules.
    inspection: Low-level inspection utilities for unwrapping decorators
        and accessing object metadata.
    module: Module loading, path conversion, and cross-package module
        discovery utilities.
    package: Package discovery, traversal, and dependency graph analysis.

The utilities support both static analysis (without importing) and dynamic
introspection (with importing), making them suitable for code generation,
testing frameworks, and package management tools.
"""
