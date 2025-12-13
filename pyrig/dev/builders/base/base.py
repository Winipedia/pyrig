"""Abstract base classes for artifact builders.

This module provides the ``Builder`` and ``PyInstallerBuilder`` abstract
base classes for creating distributable artifacts. Subclass these to
define custom build processes for your project.

The builder system uses automatic discovery: all non-abstract Builder
subclasses across packages depending on pyrig are found and invoked
when running ``pyrig build``.

Example:
    Create a custom builder by subclassing PyInstallerBuilder:

        class MyAppBuilder(PyInstallerBuilder):
            @classmethod
            def get_additional_resource_pkgs(cls) -> list[ModuleType]:
                return [my_resources_package]

Attributes:
    ARTIFACTS_DIR_NAME: Default output directory for artifacts ("dist").
"""

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
from pyrig.src.modules.class_ import (
    get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep,
)
from pyrig.src.modules.module import (
    to_path,
)


class Builder(ABC):
    """Abstract base class for artifact builders.

    Subclass this class and implement ``create_artifacts`` to define
    a custom build process. The build is triggered automatically when
    the class is instantiated.

    Subclasses must implement:
        - ``create_artifacts``: Create artifacts in the provided temp directory

    Attributes:
        ARTIFACTS_DIR_NAME: Output directory name for built artifacts.

    Example:
        class MyBuilder(Builder):
            @classmethod
            def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
                # Create your artifacts here
                pass

        if __name__ == "__main__":
            MyBuilder()
    """

    ARTIFACTS_DIR_NAME = "dist"

    @classmethod
    @abstractmethod
    def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
        """Create artifacts in the temporary directory.

        Subclasses must implement this method to define the build process.
        All artifacts should be written to ``temp_artifacts_dir``.

        Args:
            temp_artifacts_dir: Temporary directory where artifacts should
                be created. Contents will be moved to the final output
                directory after the build completes.
        """

    def __init__(self) -> None:
        """Initialize the builder and trigger the build process."""
        self.__class__.build()

    @classmethod
    def get_artifacts_dir(cls) -> Path:
        """Get the final output directory for artifacts.

        Returns:
            Path to the artifacts directory (default: "dist").
        """
        return Path(cls.ARTIFACTS_DIR_NAME)

    @classmethod
    def build(cls) -> None:
        """Execute the build process.

        Creates a temporary directory, invokes ``create_artifacts``,
        then moves and renames artifacts to the final output directory
        with platform-specific suffixes.
        """
        with tempfile.TemporaryDirectory() as temp_build_dir:
            temp_dir_path = Path(temp_build_dir)
            temp_artifacts_dir = cls.get_temp_artifacts_path(temp_dir_path)
            cls.create_artifacts(temp_artifacts_dir)
            artifacts = cls.get_temp_artifacts(temp_artifacts_dir)
            cls.rename_artifacts(artifacts)

    @classmethod
    def rename_artifacts(cls, artifacts: list[Path]) -> None:
        """Move artifacts to output directory with platform-specific names.

        Args:
            artifacts: List of artifact paths to rename and move.
        """
        artifacts_dir = cls.get_artifacts_dir()
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        for artifact in artifacts:
            # rename the files with -platform.system()
            new_name = f"{artifact.stem}-{platform.system()}{artifact.suffix}"
            new_path = artifacts_dir / new_name
            shutil.move(str(artifact), str(new_path))

    @classmethod
    def get_temp_artifacts(cls, temp_artifacts_dir: Path) -> list[Path]:
        """Get all artifacts from the temporary build directory.

        Args:
            temp_artifacts_dir: Path to the temporary artifacts directory.

        Returns:
            List of paths to built artifacts.

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
            List of paths to built artifacts in the output directory.
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
        """Discover all non-abstract Builder subclasses.

        Searches all packages depending on pyrig for Builder subclasses.
        Parent classes are discarded so only leaf implementations are returned.

        Returns:
            List of non-abstract Builder subclass types.
        """
        return get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep(
            cls,
            pyrig,
            builders,
            discard_parents=True,
        )

    @classmethod
    def init_all_non_abstract_subclasses(cls) -> None:
        """Instantiate all discovered Builder subclasses to trigger builds."""
        for builder_cls in cls.get_non_abstract_subclasses():
            builder_cls()

    @classmethod
    def get_app_name(cls) -> str:
        """Get the application name from pyproject.toml.

        Returns:
            The project name as defined in pyproject.toml.
        """
        return PyprojectConfigFile.get_project_name()

    @classmethod
    def get_root_path(cls) -> Path:
        """Get the project root directory path.

        Returns:
            Path to the project root (parent of the source package).
        """
        src_pkg = get_src_package()
        return to_path(src_pkg, is_package=True).resolve().parent

    @classmethod
    def get_main_path(cls) -> Path:
        """Get the absolute path to the main.py entry point.

        Returns:
            Path to the main.py file in the source package.
        """
        return cls.get_src_pkg_path() / cls.get_main_path_from_src_pkg()

    @classmethod
    def get_resources_path(cls) -> Path:
        """Get the absolute path to the resources directory.

        Returns:
            Path to the dev/artifacts/resources directory.
        """
        return cls.get_src_pkg_path() / cls.get_resources_path_from_src_pkg()

    @classmethod
    def get_src_pkg_path(cls) -> Path:
        """Get the absolute path to the source package.

        Returns:
            Path to the source package directory.
        """
        return cls.get_root_path() / PyprojectConfigFile.get_package_name()

    @classmethod
    def get_main_path_from_src_pkg(cls) -> Path:
        """Get the relative path to main.py from the source package.

        Returns:
            Relative path from source package to main.py.
        """
        return to_path(main, is_package=False).relative_to(
            to_path(pyrig, is_package=True)
        )

    @classmethod
    def get_resources_path_from_src_pkg(cls) -> Path:
        """Get the relative path to resources from the source package.

        Returns:
            Relative path from source package to resources directory.
        """
        return to_path(resources, is_package=True).relative_to(
            to_path(pyrig, is_package=True)
        )
