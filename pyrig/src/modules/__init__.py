"""Python module and package introspection utilities.

Provides utilities for module discovery, class introspection, function extraction, and
package traversal. Powers pyrig's automatic discovery of ConfigFile subclasses,
BuilderConfigFile implementations, and test fixtures across multiple packages.

Modules:
    class_: Class introspection, method extraction, subclass discovery
    function: Function detection and extraction from modules
    imports: Dynamic module and package importing with fallback
    inspection: Low-level inspection (unwrapping, metadata, signatures)
    module: Module loading, path conversion, cross-package discovery
    package: Package discovery, traversal, dependency graph analysis
    path: Module name ↔ file path conversion (PyInstaller-aware)
"""
