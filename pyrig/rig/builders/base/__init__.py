"""Base class for artifact builders.

Provides the abstract `BuilderConfigFile` base class that defines the interface
and orchestration logic for all artifact builders. The `BuilderConfigFile` class
handles the complete build lifecycle including temporary directory management,
artifact creation, platform-specific renaming, and automatic cleanup. Subclasses
must implement `create_artifacts(self, temp_artifacts_dir: Path) -> None`.
"""
