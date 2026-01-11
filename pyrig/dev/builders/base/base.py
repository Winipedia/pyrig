"""Base builder module for artifact generation.

This module provides the abstract base class for all builders in the pyrig framework.
Builders are specialized configuration file handlers that create build artifacts
(executables, documentation, packages, etc.) rather than configuration files.

The :class:`BuilderConfigFile` extends :class:`ConfigFile` but repurposes its
interface for build operations:

- ``load()`` returns existing artifacts from the output directory
- ``dump()`` triggers the build process
- ``create_file()`` creates the output directory structure

Subclasses implement :meth:`~BuilderConfigFile.create_artifacts` to define their
specific build logic. The framework handles temporary directory management,
artifact collection, and platform-specific naming.

Example:
    ::

        class MyBuilder(BuilderConfigFile):
            @classmethod
            def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
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
from pyrig.dev import builders
from pyrig.dev.configs.base.list_cf import ListConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.path import ModulePath

logger = logging.getLogger(__name__)


class BuilderConfigFile(ListConfigFile):
    """Abstract base class for artifact builders.

    BuilderConfigFile provides a framework for creating build artifacts with
    platform-specific naming and organized output. It extends ListConfigFile but
    adapts its interface for build operations rather than configuration management.

    The build lifecycle:

    1. A temporary directory is created
    2. :meth:`create_artifacts` is called (implemented by subclasses)
    3. Artifacts are collected from the temporary directory
    4. Artifacts are renamed with platform suffixes (e.g., ``-Linux``, ``-Windows``)
    5. Artifacts are moved to the final output directory (default: ``dist/``)

    Subclasses must implement :meth:`create_artifacts` to define their build logic.

    Attributes:
        ARTIFACTS_DIR_NAME: Default output directory name (``"dist"``).

    Example:
        ::

            class ExecutableBuilder(BuilderConfigFile):
                @classmethod
                def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
                    exe_path = temp_artifacts_dir / f"{cls.get_app_name()}.exe"
                    # ... compile and create executable ...

    See Also:
        :class:`~pyrig.dev.configs.base.list_cf.ListConfigFile`: Parent class providing
            the list-based configuration file interface.
    """

    ARTIFACTS_DIR_NAME = "dist"

    @classmethod
    @abstractmethod
    def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
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
            ::

                @classmethod
                def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
                    output = temp_artifacts_dir / "docs.zip"
                    output.write_text("documentation")
        """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for artifacts.

        For builders, this is the directory where artifacts are stored. The default
        is "dist", but can be overridden by subclasses.

        Returns:
            Path to the artifacts directory (e.g., "dist").
        """
        return Path(cls.ARTIFACTS_DIR_NAME)

    @classmethod
    def _load(cls) -> list[Path]:
        """Get all artifacts from the output directory.

        Returns:
            List of artifact paths (non-recursive).
        """
        return list(cls.get_parent_path().glob("*"))

    @classmethod
    def _dump(cls, config: list[Path]) -> None:  # noqa: ARG003
        """Build artifacts.

        Args:
            config: Ignored. Required by parent class interface.
        """
        cls.build()

    @classmethod
    def get_file_extension(cls) -> str:
        """Return empty string (builders don't use file extensions)."""
        return ""

    @classmethod
    def _get_configs(cls) -> list[Path]:
        """Return empty list (builders don't use config lists)."""
        return []

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the builder has created any artifacts.

        Returns:
            True if at least one artifact was created and exists.
        """
        return bool(cls.load())

    @classmethod
    def create_file(cls) -> None:
        """Create the parent directory for artifacts.

        Not creating the file itself, as the file creation is handled by the
        create_artifacts() method.
        """
        cls.get_parent_path().mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_definition_pkg(cls) -> ModuleType:
        """Get the package where the BuilderConfigFile subclasses are to be defined.

        Default is pyrig.dev.builders, which overrides the default pyrig.dev.configs.
        But can be overridden by subclasses to define their own package.

        Returns:
            Package module where the BuilderConfigFile subclass is defined.
        """
        return builders

    @classmethod
    def build(cls) -> None:
        """Execute the complete build process.

        Main orchestration method that manages the build lifecycle: creates a
        temporary directory, invokes `create_artifacts`, collects artifacts,
        renames them with platform-specific suffixes, and moves them to the
        final output directory.

        See Also:
            create_artifacts: Subclass-implemented method that creates artifacts
            rename_artifacts: Adds platform suffixes and moves to output
        """
        logger.debug("Building artifacts with %s", cls.__name__)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_artifacts_dir = cls.get_temp_artifacts_path(temp_dir_path)
            cls.create_artifacts(temp_artifacts_dir)
            artifacts = cls.get_temp_artifacts(temp_artifacts_dir)
            cls.rename_artifacts(artifacts)
        logger.debug("Built %d artifact(s) with %s", len(artifacts), cls.__name__)

    @classmethod
    def rename_artifacts(cls, artifacts: list[Path]) -> None:
        """Move artifacts to output directory with platform-specific names.

        Renames artifacts with platform-specific suffixes (`-Linux`, `-Windows`,
        `-Darwin`) and moves them to the final output directory.

        Args:
            artifacts: List of artifact paths from the temporary directory.
        """
        for artifact in artifacts:
            cls.rename_artifact(artifact)

    @classmethod
    def rename_artifact(cls, artifact: Path) -> None:
        """Rename a single artifact with platform-specific suffix.

        Args:
            artifact: Path to the artifact.
        """
        platform_specific_path = cls.get_platform_specific_path(artifact)
        logger.debug("Moving artifact: %s to: %s", artifact, platform_specific_path)
        shutil.move(str(artifact), str(platform_specific_path))
        logger.info("Created artifact: %s", platform_specific_path.name)

    @classmethod
    def get_platform_specific_path(cls, artifact: Path) -> Path:
        """Get the platform-specific path for an artifact.

        Args:
            artifact: Path to the artifact.

        Returns:
            Platform-specific path for the artifact.
        """
        return cls.get_parent_path() / cls.get_platform_specific_name(artifact)

    @classmethod
    def get_platform_specific_name(cls, artifact: Path) -> str:
        """Get the platform-specific name for an artifact.

        Args:
            artifact: Path to the artifact.

        Returns:
            Platform-specific name for the artifact.
        """
        return f"{artifact.stem}-{platform.system()}{artifact.suffix}"

    @classmethod
    def get_temp_artifacts(cls, temp_artifacts_dir: Path) -> list[Path]:
        """Get all artifacts from the temporary build directory.

        Args:
            temp_artifacts_dir: Path to the temporary artifacts directory.

        Returns:
            List of artifact paths (non-recursive). May be empty if no
            artifacts were created.
        """
        return list(temp_artifacts_dir.glob("*"))

    @classmethod
    def get_temp_artifacts_path(cls, temp_dir: Path) -> Path:
        """Create and return the temporary artifacts subdirectory.

        Args:
            temp_dir: Parent temporary directory.

        Returns:
            Path to the created artifacts subdirectory.
        """
        path = temp_dir / cls.ARTIFACTS_DIR_NAME
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_app_name(cls) -> str:
        """Get the application name from pyproject.toml.

        Returns:
            Project name from pyproject.toml.
        """
        return PyprojectConfigFile.L.get_project_name()

    @classmethod
    def get_root_path(cls) -> Path:
        """Get the project root directory path.

        Returns:
            Absolute path to the project root directory.
        """
        src_pkg = import_module(PyprojectConfigFile.L.get_package_name())
        src_path = ModulePath.pkg_type_to_dir_path(src_pkg)
        return src_path.parent

    @classmethod
    def get_main_path(cls) -> Path:
        """Get the absolute path to the main.py entry point.

        Returns:
            Absolute path to main.py.
        """
        return cls.get_src_pkg_path() / cls.get_main_path_relative_to_src_pkg()

    @classmethod
    def get_resources_path(cls) -> Path:
        """Get the absolute path to the resources directory.

        Returns:
            Absolute path to the resources directory.
        """
        return cls.get_src_pkg_path() / cls.get_resources_path_relative_to_src_pkg()

    @classmethod
    def get_src_pkg_path(cls) -> Path:
        """Get the absolute path to the source package.

        Returns:
            Absolute path to the source package directory.
        """
        return cls.get_root_path() / PyprojectConfigFile.L.get_package_name()

    @classmethod
    def get_main_path_relative_to_src_pkg(cls) -> Path:
        """Get the relative path to main.py from the source package.

        Returns:
            Relative path from source package to main.py.
        """
        project_main_file = ModulePath.module_name_to_relative_file_path(main.__name__)
        pyrig_pkg_dir = ModulePath.pkg_name_to_relative_dir_path(pyrig.__name__)
        return project_main_file.relative_to(pyrig_pkg_dir)

    @classmethod
    def get_resources_path_relative_to_src_pkg(cls) -> Path:
        """Get the relative path to resources from the source package.

        Returns:
            Relative path from source package to resources directory.
        """
        resources_path = ModulePath.pkg_name_to_relative_dir_path(resources.__name__)
        pyrig_pkg_dir = ModulePath.pkg_name_to_relative_dir_path(pyrig.__name__)
        return resources_path.relative_to(pyrig_pkg_dir)
