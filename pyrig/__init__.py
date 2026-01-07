"""pyrig - A Python toolkit to rig up your project.

Opinionated Python project toolkit that standardizes and automates project setup,
configuration, and development.

Subpackages:
    src: Runtime utilities available in production environments.
        Includes project name extraction (cli), Git utilities (git),
        directed graph (graph), nested structure validation (iterate),
        resource access (resource), string manipulation (string),
        module introspection (modules), and subprocess execution (processes).
    dev: Development-time tools requiring dev dependencies.
        Includes artifact builders (builders), CLI framework and commands (cli),
        configuration file system (configs), tool wrappers (management),
        test infrastructure (tests), and development utilities (utils).
    resources: Static resource files (templates, licenses, data files).
        Accessible via get_resource_path(name, package) from pyrig.src.resource.
"""
