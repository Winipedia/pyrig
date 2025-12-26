"""Base classes for artifact builders.

This package provides the abstract `Builder` base class that defines the
interface and orchestration logic for all artifact builders in the pyrig
ecosystem.

The Builder class implements the complete build lifecycle:
    1. Temporary directory creation and management
    2. Artifact creation via subclass-implemented `create_artifacts()`
    3. Artifact collection and validation
    4. Platform-specific renaming (adds `-Linux`, `-Windows`, or `-Darwin` suffix)
    5. Moving artifacts to final output directory (`dist/` by default)
    6. Automatic cleanup of temporary directories

The class also provides automatic discovery of all concrete Builder subclasses
across packages depending on pyrig, enabling the `pyrig build` command to find
and execute all builders in the dependency chain.

Classes:
    Builder: Abstract base class for all artifact builders. Subclasses must
        implement `create_artifacts(cls, temp_artifacts_dir: Path) -> None`.

See Also:
    pyrig.dev.builders.base.base.Builder: Full Builder class implementation
    pyrig.dev.builders.pyinstaller.PyInstallerBuilder: PyInstaller builder
"""
