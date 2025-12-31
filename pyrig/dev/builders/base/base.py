"""Abstract base class for artifact builders.

Provides the `Builder` abstract base class that defines the interface and
orchestration logic for creating distributable artifacts from pyrig projects.

Build Lifecycle:
    1. Create temporary build directory
    2. Create artifacts subdirectory within temp directory
    3. Invoke subclass's `create_artifacts()` method
    4. Collect all files created in the artifacts subdirectory
    5. Rename artifacts with platform suffixes (`-Linux`, `-Windows`, `-Darwin`)
    6. Move renamed artifacts to final output directory (`dist/` by default)
    7. Clean up temporary directory automatically

The builder system uses pyrig's multi-package architecture to automatically
discover all non-abstract Builder subclasses across packages depending on pyrig.
When `pyrig build` is executed, all discovered builders are instantiated
sequentially, triggering their build process.

Example:
    Create a custom builder::

        from pathlib import Path
        from pyrig.dev.builders.base.base import Builder

        class DocumentationBuilder(Builder):
            '''Builder for creating documentation archives.'''

            @classmethod
            def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
                docs_archive = temp_artifacts_dir / "docs.zip"
                # Build documentation and create archive
                docs_archive.write_text("documentation content")

    Build all artifacts::

        $ uv run pyrig build
        # Creates: dist/docs-Linux.zip (or platform-specific name)

Module Attributes:
    logger: Logger instance for builder operations.

See Also:
    pyrig.dev.builders.pyinstaller.PyInstallerBuilder: PyInstaller builder
    pyrig.dev.cli.commands.build_artifacts.build_artifacts: Build command
"""

import logging
import platform
import shutil
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

import pyrig
from pyrig import main, resources
from pyrig.dev import builders
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.utils.packages import get_src_package
from pyrig.src.modules.package import (
    get_all_subcls_from_mod_in_all_deps_depen_on_dep,
)
from pyrig.src.modules.path import ModulePath

logger = logging.getLogger(__name__)


class Builder(ABC):
    """Abstract base class for artifact builders.

    Provides the framework for creating distributable artifacts from pyrig projects.
    Subclasses implement `create_artifacts` to define their build logic. The build
    process is automatically triggered when the builder is instantiated.

    Handles all build orchestration including temporary directory management,
    artifact collection and validation, platform-specific naming, and moving
    artifacts to the final output directory. Supports automatic discovery across
    dependent packages.

    Subclasses must implement:
        create_artifacts: Create artifacts in the provided temporary directory.

    Attributes:
        ARTIFACTS_DIR_NAME: Output directory name for built artifacts (default: "dist").

    Example:
        Basic builder implementation::

            from pathlib import Path
            from pyrig.dev.builders.base.base import Builder

            class MyBuilder(Builder):
                @classmethod
                def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
                    artifact = temp_artifacts_dir / "my-artifact.tar.gz"
                    artifact.write_bytes(b"artifact content")

        Trigger build::

            MyBuilder()  # Automatically builds and outputs to dist/
            # Or: uv run pyrig build

    See Also:
        create_artifacts: Abstract method that subclasses must implement
        build: Main build orchestration method
        get_non_abstract_subclasses: Discovery mechanism for finding builders
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

    def __init__(self) -> None:
        """Initialize the builder and trigger the build process.

        Instantiating a Builder subclass automatically triggers the build process.
        The build runs synchronously and completes before this constructor returns.
        """
        self.__class__.build()

    @classmethod
    def get_artifacts_dir(cls) -> Path:
        """Get the final output directory for artifacts.

        Returns:
            Path to the artifacts output directory (default: "dist").
        """
        return Path(cls.ARTIFACTS_DIR_NAME)

    @classmethod
    def build(cls) -> None:
        """Execute the complete build process.

        Main orchestration method that manages the build lifecycle: creates a
        temporary directory, invokes `create_artifacts`, collects artifacts,
        renames them with platform-specific suffixes, and moves them to the
        final output directory.

        Raises:
            FileNotFoundError: If `create_artifacts` doesn't create any files.

        See Also:
            create_artifacts: Subclass-implemented method that creates artifacts
            rename_artifacts: Adds platform suffixes and moves to output
        """
        logger.debug("Building artifacts with %s", cls.__name__)
        with tempfile.TemporaryDirectory() as temp_build_dir:
            temp_dir_path = Path(temp_build_dir)
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
        artifacts_dir = cls.get_artifacts_dir()
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        for artifact in artifacts:
            new_name = f"{artifact.stem}-{platform.system()}{artifact.suffix}"
            new_path = artifacts_dir / new_name
            logger.debug("Moving artifact: %s to: %s", artifact, new_path)
            shutil.move(str(artifact), str(new_path))
            logger.info("Created artifact: %s", new_path.name)

    @classmethod
    def get_temp_artifacts(cls, temp_artifacts_dir: Path) -> list[Path]:
        """Get all artifacts from the temporary build directory.

        Args:
            temp_artifacts_dir: Path to the temporary artifacts directory.

        Returns:
            List of artifact paths (non-recursive).

        Raises:
            FileNotFoundError: If no artifacts were created.
        """
        paths = list(temp_artifacts_dir.glob("*"))
        if not paths:
            msg = f"Expected {temp_artifacts_dir} to contain files"
            raise FileNotFoundError(msg)
        return paths

    @classmethod
    def get_artifacts(cls) -> list[Path]:
        """Get all artifacts from the final output directory.

        Returns:
            List of artifact paths from the output directory.
        """
        return list(cls.get_artifacts_dir().glob("*"))

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
    def get_non_abstract_subclasses(cls) -> list[type["Builder"]]:
        """Discover all non-abstract Builder subclasses across dependent packages.

        Uses pyrig's multi-package architecture to find all concrete Builder
        subclasses across packages that depend on pyrig. Searches for `dev.builders`
        modules in each package and returns only non-abstract leaf classes.

        Returns:
            List of concrete Builder subclass types (not instances).

        See Also:
            init_all_non_abstract_subclasses: Instantiates all discovered builders
        """
        return get_all_subcls_from_mod_in_all_deps_depen_on_dep(
            cls,
            pyrig,
            builders,
            discard_parents=True,
            exclude_abstract=True,
        )

    @classmethod
    def init_all_non_abstract_subclasses(cls) -> None:
        """Instantiate all discovered Builder subclasses to trigger builds.

        Discovers all non-abstract Builder subclasses across packages depending
        on pyrig and instantiates each one sequentially. This is the implementation
        of the `pyrig build` command.

        See Also:
            get_non_abstract_subclasses: Discovery mechanism for finding builders
        """
        builders = cls.get_non_abstract_subclasses()
        for builder_cls in builders:
            builder_cls()

    @classmethod
    def get_app_name(cls) -> str:
        """Get the application name from pyproject.toml.

        Returns:
            Project name from pyproject.toml.
        """
        return PyprojectConfigFile.get_project_name()

    @classmethod
    def get_root_path(cls) -> Path:
        """Get the project root directory path.

        Returns:
            Absolute path to the project root directory.
        """
        src_pkg = get_src_package()
        src_path = ModulePath.pkg_type_to_dir_path(src_pkg)
        return src_path.parent

    @classmethod
    def get_main_path(cls) -> Path:
        """Get the absolute path to the main.py entry point.

        Returns:
            Absolute path to main.py.
        """
        return cls.get_src_pkg_path() / cls.get_main_path_from_src_pkg()

    @classmethod
    def get_resources_path(cls) -> Path:
        """Get the absolute path to the resources directory.

        Returns:
            Absolute path to the resources directory.
        """
        return cls.get_src_pkg_path() / cls.get_resources_path_from_src_pkg()

    @classmethod
    def get_src_pkg_path(cls) -> Path:
        """Get the absolute path to the source package.

        Returns:
            Absolute path to the source package directory.
        """
        return cls.get_root_path() / PyprojectConfigFile.get_package_name()

    @classmethod
    def get_main_path_from_src_pkg(cls) -> Path:
        """Get the relative path to main.py from the source package.

        Returns:
            Relative path from source package to main.py.
        """
        project_main_file = ModulePath.module_name_to_relative_file_path(main.__name__)
        pyrig_pkg_dir = ModulePath.pkg_name_to_relative_dir_path(pyrig.__name__)
        return project_main_file.relative_to(pyrig_pkg_dir)

    @classmethod
    def get_resources_path_from_src_pkg(cls) -> Path:
        """Get the relative path to resources from the source package.

        Returns:
            Relative path from source package to resources directory.
        """
        resources_path = ModulePath.pkg_name_to_relative_dir_path(resources.__name__)
        pyrig_pkg_dir = ModulePath.pkg_name_to_relative_dir_path(pyrig.__name__)
        return resources_path.relative_to(pyrig_pkg_dir)
