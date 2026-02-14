"""pyrig - A Python toolkit to rig up your project.

Opinionated Python project toolkit that standardizes and automates project setup,
configuration, and development.

Subpackages:
    src: Runtime utilities available in production environments.
        Includes CLI utilities (cli), Git utilities (git),
        directed graph (graph), package dependency graph (dependency_graph),
        nested structure validation (iterate), subprocess execution (processes),
        network connectivity checking (requests), resource access (resource),
        singleton pattern (singleton), string manipulation (string_),
        subclass discovery (subclass), and module introspection (modules).
    rig: Development-time tools requiring dev dependencies.
        Includes artifact builders (builders), CLI framework and commands (cli),
        configuration file system (configs), tool wrappers (tools),
        test infrastructure (tests), and development utilities (utils).
    resources: Static resource files (templates, licenses, data files).
        Accessible via resource_path(name, package) from pyrig.src.resource.
"""
