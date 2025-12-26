"""Artifact builder infrastructure for creating distributable packages.

This package provides the builder system for creating distributable artifacts
from pyrig projects. Builders are automatically discovered across all packages
depending on pyrig and executed sequentially when running `pyrig build`.

Architecture Overview:
    The builder system uses pyrig's multi-package discovery mechanism to find
    all concrete Builder subclasses across the dependency graph. When a builder
    is instantiated, it automatically triggers its build process via `__init__`,
    creating artifacts in a temporary directory before moving them to the final
    output location with platform-specific naming.

    Build execution is **sequential**, not parallel. Each builder completes
    before the next one starts.

Class Hierarchy:
    The builder system provides a two-tier abstract class hierarchy:

    1. **Builder** (abstract base class): Provides build orchestration framework,
       temporary directory management, artifact collection, and platform-specific
       renaming. Subclasses must implement `create_artifacts()`.

    2. **PyInstallerBuilder** (abstract): Extends Builder with PyInstaller-specific
       functionality including resource bundling, icon conversion, and executable
       creation. Subclasses must implement `get_additional_resource_pkgs()`.

    Concrete builders must inherit from one of these and implement the required
    abstract methods.

Key Features:
    - **Automatic discovery**: Finds all Builder subclasses across dependent
      packages using pyrig's module discovery system
    - **PyInstaller support**: Built-in abstract builder for creating standalone
      executables with automatic resource bundling
    - **Resource bundling**: Automatically collects and bundles resource files
      from multiple packages in the dependency chain
    - **Platform-specific naming**: Adds platform suffixes to artifacts
      (e.g., `-Linux`, `-Windows`, `-Darwin`)
    - **Temporary directory management**: Builds in isolated temp directories
      with automatic cleanup
    - **Extensible**: Create custom builders by subclassing Builder or
      PyInstallerBuilder

Build Process Flow:
    1. User runs `uv run pyrig build`
    2. Command calls `Builder.init_all_non_abstract_subclasses()`
    3. Discovery finds all concrete Builder subclasses across packages
    4. Each builder is instantiated sequentially
    5. Instantiation triggers `__init__` → `build()` → `create_artifacts()`
    6. Artifacts are collected, renamed with platform suffix, and moved to `dist/`
    7. Temporary directories are cleaned up automatically

Example:
    Create a custom PyInstaller builder::

        from pyrig.dev.builders.pyinstaller import PyInstallerBuilder
        from types import ModuleType
        import myapp.resources

        class MyAppBuilder(PyInstallerBuilder):
            '''Builder for creating MyApp standalone executable.'''

            @classmethod
            def get_additional_resource_pkgs(cls) -> list[ModuleType]:
                '''Specify additional resource packages to bundle.'''
                return [myapp.resources]

    Build all artifacts::

        $ uv run pyrig build

    This discovers MyAppBuilder and any other builders, then creates artifacts
    like `dist/myapp-Linux` (or platform-specific equivalent).

See Also:
    pyrig.dev.builders.base.base.Builder: Base class for all builders
    pyrig.dev.builders.pyinstaller.PyInstallerBuilder: PyInstaller builder
    pyrig.dev.cli.commands.build_artifacts: Build command implementation
"""
