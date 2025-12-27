"""Artifact builder infrastructure for creating distributable packages.

This package provides the builder system for creating distributable artifacts
from pyrig projects. Builders are automatically discovered across all packages
depending on pyrig and executed sequentially when running `pyrig build`.

Architecture:
    The builder system uses pyrig's multi-package discovery to find all concrete
    Builder subclasses across the dependency graph. Instantiating a builder
    automatically triggers its build process, creating artifacts in a temporary
    directory before moving them to the final output location with platform-specific
    naming. Builds execute sequentially, not in parallel.

Class Hierarchy:
    - **Builder** (abstract): Build orchestration, temp directory management,
      artifact collection, and platform-specific renaming. Subclasses implement
      `create_artifacts()`.
    - **PyInstallerBuilder** (abstract): Extends Builder with PyInstaller-specific
      functionality including resource bundling, icon conversion, and executable
      creation. Subclasses implement `get_additional_resource_pkgs()`.

Key Features:
    - Automatic discovery across dependent packages
    - PyInstaller support with resource bundling
    - Platform-specific naming (`-Linux`, `-Windows`, `-Darwin`)
    - Temporary directory management with automatic cleanup
    - Extensible via subclassing

Build Process:
    1. Run `uv run pyrig build`
    2. Discovery finds all concrete Builder subclasses
    3. Each builder is instantiated sequentially
    4. Instantiation triggers `__init__` → `build()` → `create_artifacts()`
    5. Artifacts are renamed with platform suffix and moved to `dist/`
    6. Temporary directories are cleaned up

Example:
    Create a custom PyInstaller builder::

        from pyrig.dev.builders.pyinstaller import PyInstallerBuilder
        from types import ModuleType
        import myapp.resources

        class MyAppBuilder(PyInstallerBuilder):
            '''Builder for MyApp standalone executable.'''

            @classmethod
            def get_additional_resource_pkgs(cls) -> list[ModuleType]:
                return [myapp.resources]

    Build all artifacts::

        $ uv run pyrig build

See Also:
    pyrig.dev.builders.base.base.Builder: Base class for all builders
    pyrig.dev.builders.pyinstaller.PyInstallerBuilder: PyInstaller builder
    pyrig.dev.cli.commands.build_artifacts: Build command implementation
"""
