"""Runtime utilities and source code infrastructure for pyrig.

Production-ready utilities for runtime use with minimal dependencies. Unlike `pyrig.dev`
(development-only tools), `pyrig.src` is designed for use in production code.

Modules:
    cli: CLI argument parsing and project name extraction
    consts: Constants (standard development dependencies)
    git: Repository URL parsing and GitHub integration
    graph: Directed graph for dependency analysis
    iterate: Nested structure comparison and validation
    resource: PyInstaller-compatible resource file loading
    string: Naming convention transformations

Subpackages:
    management: Project initialization and management
    modules: Module/package introspection and discovery
    os: Subprocess execution and command discovery
    testing: Test generation and assertion helpers

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
