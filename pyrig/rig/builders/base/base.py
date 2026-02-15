"""Base builder module for artifact generation.

This module provides the abstract base class for all builders in the pyrig framework.
Builders are specialized configuration file handlers that create build artifacts
(executables, documentation, packages, etc.) rather than configuration files.

`BuilderConfigFile` extends `ListConfigFile` but repurposes its interface for build
operations:

- `load()` returns existing artifacts from the output directory
- `dump()` triggers the build process
- `create_file()` creates the output directory structure

Subclasses implement `create_artifacts()` to define their specific build logic.
The framework handles temporary directory management, artifact collection, and
platform-specific naming.

Example:
    Basic builder implementation:

        class MyBuilder(BuilderConfigFile):

            def create_artifacts(self, temp_artifacts_dir: Path) -> None:
                output = temp_artifacts_dir / "my_app.exe"
                # ... build logic ...
                output.write_bytes(b"executable content")
"""

import logging
import platform
import shutil
import tempfile
from abc import abstractmethod
from importlib import import_module
from pathlib import Path
from types import ModuleType

import pyrig
from pyrig import main, resources
from pyrig.rig import builders
from pyrig.rig.configs.base.list_cf import ListConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.path import ModulePath

logger = logging.getLogger(__name__)


class BuilderConfigFile(ListConfigFile):
    """Abstract base class for artifact builders.

    BuilderConfigFile provides a framework for creating build artifacts with
    platform-specific naming and organized output. It extends ListConfigFile but
    adapts its interface for build operations rather than configuration management.

    The build lifecycle:

    1. A temporary directory is created
    2. `create_artifacts` is called (implemented by subclasses)
    3. Artifacts are collected from the temporary directory
    4. Artifacts are renamed with platform suffixes (e.g., ``-Linux``, ``-Windows``)
    5. Artifacts are moved to the final output directory (default: ``dist/``)

    Subclasses must implement `create_artifacts` to define their build logic.

    Example:
        Basic builder subclass:

            class ExecutableBuilder(BuilderConfigFile):

                def create_artifacts(self, temp_artifacts_dir: Path) -> None:
                    exe_path = temp_artifacts_dir / f"{self.app_name()}.exe"
                    # ... compile and create executable ...
    """

    @abstractmethod
    def create_artifacts(self, temp_artifacts_dir: Path) -> None:
        """Create artifacts in the temporary directory.

        Subclasses must implement this method to define their build logic. All
        artifacts should be written to the provided temporary directory. The
        Builder framework will automatically collect, rename, and move artifacts
        to the final output directory.

        Args:
            temp_artifacts_dir: Temporary directory where artifacts should be created.
                All files created here will be moved to the final output directory
                with platform-specific naming.

        Example:
            Subclass implementation:


                def create_artifacts(self, temp_artifacts_dir: Path) -> None:
                    output = temp_artifacts_dir / "docs.zip"
                    output.write_text("documentation")
        """

    @classmethod
    def definition_package(cls) -> ModuleType:
        """Get the package containing builder subclass definitions.

        Default is `pyrig.rig.builders`, overriding the base default of
        `pyrig.rig.configs`. Can be overridden by subclasses.
        """
        return builders

    def parent_path(self) -> Path:
        """Get the parent directory for artifacts.

        For builders, this is the directory where artifacts are stored. The default
        is "dist", but can be overridden by subclasses.

        Returns:
            Path to the artifacts directory (e.g., "dist").
        """
        return Path(self.dist_dir_name())

    def _load(self) -> list[Path]:
        """Get all artifacts from the output directory.

        Returns:
            List of artifact paths (non-recursive).
        """
        return list(self.parent_path().glob("*"))

    def _dump(self, config: list[Path]) -> None:  # noqa: ARG002
        """Build artifacts.

        Args:
            config: Ignored. Required by parent class interface.
        """
        self.build()

    def extension(self) -> str:
        """Return empty string (builders don't use file extensions)."""
        return ""

    def _configs(self) -> list[Path]:
        """Return empty list (builders don't use config lists)."""
        return []

    def is_correct(self) -> bool:
        """Check if the builder has created any artifacts.

        Returns:
            True if at least one artifact was created and exists.
        """
        return bool(self.load())

    def create_file(self) -> None:
        """Create the parent directory for artifacts.

        Does not create a file itself; file creation is handled by
        `create_artifacts`.
        """
        self.parent_path().mkdir(parents=True, exist_ok=True)

    @classmethod
    def dist_dir_name(cls) -> str:
        """Get the name of the artifacts directory.

        Default is "dist", but can be overridden by subclasses.
        Is a classmethod unlike the rest of the interface
        because it's used in WorkflowConfigFile subclasses and BuilderConfigFile
        itself is abstract, so it can't be instantiated to call instance methods.

        Returns:
            Name of the artifacts directory (e.g., "dist").
        """
        return "dist"

    def build(self) -> None:
        """Execute the complete build process.

        Main orchestration method that manages the build lifecycle: creates a
        temporary directory, invokes `create_artifacts`, collects artifacts,
        renames them with platform-specific suffixes, and moves them to the
        final output directory. Delegates to `create_artifacts` for the actual
        build and `rename_artifacts` for platform-specific output naming.
        """
        logger.debug("Building artifacts with %s", self.__class__.__name__)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_artifacts_dir = self.temp_artifacts_path(temp_dir_path)
            self.create_artifacts(temp_artifacts_dir)
            artifacts = self.temp_artifacts(temp_artifacts_dir)
            self.rename_artifacts(artifacts)
        logger.debug(
            "Built %d artifact(s) with %s", len(artifacts), self.__class__.__name__
        )

    def rename_artifacts(self, artifacts: list[Path]) -> None:
        """Move artifacts to output directory with platform-specific names.

        Renames artifacts with platform-specific suffixes (`-Linux`, `-Windows`,
        `-Darwin`) and moves them to the final output directory.

        Args:
            artifacts: List of artifact paths from the temporary directory.
        """
        for artifact in artifacts:
            self.rename_artifact(artifact)

    def rename_artifact(self, artifact: Path) -> None:
        """Move a single artifact to the output directory with a platform-specific name.

        Args:
            artifact: Path to the artifact in the temporary build directory.
        """
        platform_specific_path = self.platform_specific_path(artifact)
        logger.debug("Moving artifact: %s to: %s", artifact, platform_specific_path)
        # create the platform-specific path's parent directory if it doesn't exist
        platform_specific_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(artifact), str(platform_specific_path))
        logger.info("Created artifact: %s", platform_specific_path.name)

    def platform_specific_path(self, artifact: Path) -> Path:
        """Get the platform-specific output path for an artifact.

        Args:
            artifact: Path to the artifact.
        """
        return self.parent_path() / self.platform_specific_name(artifact)

    def platform_specific_name(self, artifact: Path) -> str:
        """Generate a platform-specific filename (e.g., ``myapp-Linux.exe``).

        Args:
            artifact: Path to the artifact.
        """
        return f"{artifact.stem}-{platform.system()}{artifact.suffix}"

    def temp_artifacts(self, temp_artifacts_dir: Path) -> list[Path]:
        """Get all artifacts from the temporary build directory.

        Args:
            temp_artifacts_dir: Path to the temporary artifacts directory.

        Returns:
            List of artifact paths (non-recursive). May be empty if no
            artifacts were created.
        """
        return list(temp_artifacts_dir.glob("*"))

    def temp_artifacts_path(self, temp_dir: Path) -> Path:
        """Create and return the temporary artifacts subdirectory.

        Args:
            temp_dir: Parent temporary directory.

        Returns:
            Path to the created artifacts subdirectory.
        """
        path = temp_dir / self.dist_dir_name()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def app_name(self) -> str:
        """Return the application name from pyproject.toml."""
        return PyprojectConfigFile.I.project_name()

    def root_path(self) -> Path:
        """Return the absolute path to the project root directory."""
        src_package = import_module(PyprojectConfigFile.I.package_name())
        src_path = ModulePath.package_type_to_dir_path(src_package)
        return src_path.parent

    def main_path(self) -> Path:
        """Return the absolute path to the main.py entry point."""
        return self.src_package_path() / self.main_path_relative_to_src_package()

    def resources_path(self) -> Path:
        """Return the absolute path to the resources directory."""
        return self.src_package_path() / self.resources_path_relative_to_src_package()

    def src_package_path(self) -> Path:
        """Return the absolute path to the source package directory."""
        return self.root_path() / PyprojectConfigFile.I.package_name()

    def main_path_relative_to_src_package(self) -> Path:
        """Return the relative path to main.py from the source package."""
        project_main_file = ModulePath.module_name_to_relative_file_path(main.__name__)
        pyrig_package_dir = ModulePath.package_name_to_relative_dir_path(pyrig.__name__)
        return project_main_file.relative_to(pyrig_package_dir)

    def resources_path_relative_to_src_package(self) -> Path:
        """Return the relative path to the resources directory from the src package."""
        resources_path = ModulePath.package_name_to_relative_dir_path(
            resources.__name__
        )
        pyrig_package_dir = ModulePath.package_name_to_relative_dir_path(pyrig.__name__)
        return resources_path.relative_to(pyrig_package_dir)
