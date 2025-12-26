"""Artifact builder infrastructure for creating distributable packages.

This package provides the builder system for creating distributable artifacts
from pyrig projects. Builders are automatically discovered across all packages
depending on pyrig and invoked when running the `pyrig build` command.

The builder system leverages pyrig's multi-package architecture to discover
all non-abstract Builder subclasses across the dependency graph. When a builder
is instantiated, it automatically triggers the build process, creating artifacts
in a temporary directory before moving them to the final output location with
platform-specific naming.

Features:
    - **Automatic discovery**: Finds all Builder subclasses across dependent packages
    - **PyInstaller support**: Built-in support for creating standalone executables
    - **Resource bundling**: Automatically collects and bundles resource files
    - **Platform-specific naming**: Adds platform suffixes (e.g., `-Linux`, `-Windows`)
    - **Custom build processes**: Extensible via Builder subclasses
    - **Parallel execution**: Builds can run concurrently when possible

Architecture:
    The builder system uses a two-tier class hierarchy:

    1. `Builder` (abstract base class): Provides the build orchestration framework
    2. `PyInstallerBuilder` (abstract): Specialized builder for PyInstaller executables

    Concrete builders must inherit from one of these and implement required methods.

Example:
    Create a custom PyInstaller builder::

        from pyrig.dev.builders.pyinstaller import PyInstallerBuilder
        from types import ModuleType
        import myapp.resources

        class MyAppBuilder(PyInstallerBuilder):
            '''Builder for creating MyApp standalone executable.'''

            @classmethod
            def get_additional_resource_pkgs(cls) -> list[ModuleType]:
                '''Include application resources in the executable.'''
                return [myapp.resources]

    Then build all artifacts::

        $ uv run pyrig build

    This will create `dist/myapp-Linux` (or platform-specific equivalent).

See Also:
    pyrig.dev.builders.base.base: Base Builder class and build orchestration
    pyrig.dev.builders.pyinstaller: PyInstaller-specific builder implementation
    pyrig.dev.cli.commands.build_artifacts: Build command implementation
"""
