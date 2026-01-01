"""Base classes for artifact builders.

Provides the abstract `BuilderConfigFile` base class that defines the interface
and orchestration logic for all artifact builders. The BuilderConfigFile class
handles the complete build lifecycle including temporary directory management,
artifact creation, platform-specific renaming, and automatic cleanup.

Classes:
    BuilderConfigFile: Abstract base class for artifact builders. Subclasses
        must implement `create_artifacts(cls, temp_artifacts_dir: Path) -> None`.

See Also:
    pyrig.dev.builders.base.base.BuilderConfigFile: Full class implementation
    pyrig.dev.builders.pyinstaller.PyInstallerBuilder: PyInstaller builder
"""
