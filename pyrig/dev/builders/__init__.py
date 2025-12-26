"""Artifact builder infrastructure for creating distributable packages.

This package provides the builder system for creating distributable artifacts
from pyrig projects. Builders are automatically discovered and invoked when
running `pyrig build`.

The builder system supports:
- PyInstaller executables (cross-platform standalone binaries)
- Custom build processes via Builder subclasses
- Automatic resource bundling
- Platform-specific artifact naming

Key Classes:
    - `Builder`: Abstract base class for all builders
    - `PyInstallerBuilder`: Builder for creating PyInstaller executables

Example:
    Create a custom builder by subclassing PyInstallerBuilder::

        from pyrig.dev.builders.pyinstaller import PyInstallerBuilder
        from types import ModuleType

        class MyAppBuilder(PyInstallerBuilder):
            @classmethod
            def get_additional_resource_pkgs(cls) -> list[ModuleType]:
                import myapp.resources
                return [myapp.resources]

    Then run: `uv run myapp build`

See Also:
    - `pyrig.dev.builders.base.base`: Base builder classes
    - `pyrig.dev.builders.pyinstaller`: PyInstaller builder implementation
"""
