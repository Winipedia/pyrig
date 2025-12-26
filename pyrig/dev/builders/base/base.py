"""Abstract base class for artifact builders.

This module provides the `Builder` abstract base class that defines the
interface and orchestration logic for creating distributable artifacts from
pyrig projects.

The Builder class implements a complete build lifecycle:
    1. Creates a temporary build directory via `tempfile.TemporaryDirectory()`
    2. Creates an artifacts subdirectory within the temp directory
    3. Invokes the subclass's `create_artifacts()` method
    4. Collects all files created in the artifacts subdirectory
    5. Renames artifacts with platform-specific suffixes (e.g., `-Linux`)
    6. Moves renamed artifacts to the final output directory (`dist/` by default)
    7. Cleans up temporary directory automatically (via context manager)

The builder system leverages pyrig's multi-package architecture to automatically
discover all non-abstract Builder subclasses across packages depending on pyrig.
When `pyrig build` is executed, all discovered builders are instantiated
**sequentially** (not in parallel), which triggers their build process.

Build Process Flow:
    1. Builder subclass is instantiated (e.g., `MyBuilder()`)
    2. `__init__()` calls `cls.build()` automatically
    3. `build()` creates temporary directory via context manager
    4. `build()` creates artifacts subdirectory via `get_temp_artifacts_path()`
    5. `build()` calls `create_artifacts()` (implemented by subclass)
    6. `build()` collects artifacts via `get_temp_artifacts()`
    7. `build()` renames and moves artifacts via `rename_artifacts()`
    8. Temporary directory is cleaned up automatically when context exits

Platform-Specific Naming:
    Artifacts are automatically renamed with platform suffixes determined by
    `platform.system()`:
    - Linux: `artifact-Linux` (e.g., `myapp-Linux`)
    - Windows: `artifact-Windows` (e.g., `myapp-Windows.exe`)
    - macOS: `artifact-Darwin` (e.g., `myapp-Darwin`)

    The suffix is inserted before the file extension if one exists:
    - `docs.zip` → `docs-Linux.zip`
    - `myapp` → `myapp-Linux`

Example:
    Create a custom builder::

        from pathlib import Path
        from pyrig.dev.builders.base.base import Builder

        class DocumentationBuilder(Builder):
            '''Builder for creating documentation archives.'''

            @classmethod
            def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
                '''Generate documentation and create archive.'''
                docs_archive = temp_artifacts_dir / "docs.zip"
                # Build documentation and create archive
                docs_archive.write_text("documentation content")

    The builder is automatically discovered and invoked::

        $ uv run pyrig build
        # Creates: dist/docs-Linux.zip (or platform-specific name)

Module Attributes:
    logger (logging.Logger): Logger instance for builder operations. Uses the
        module's `__name__` for the logger name.

See Also:
    pyrig.dev.builders.pyinstaller.PyInstallerBuilder: PyInstaller builder
    pyrig.dev.cli.commands.build_artifacts.build_artifacts: Build command
    pyrig.src.modules.package.get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep:
        Discovery mechanism for finding builder subclasses
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
    get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep,
)
from pyrig.src.modules.path import ModulePath

logger = logging.getLogger(__name__)


class Builder(ABC):
    """Abstract base class for artifact builders.

    This class provides the framework for creating distributable artifacts
    from pyrig projects. Subclasses must implement the `create_artifacts`
    method to define their specific build logic. The build process is
    automatically triggered when the builder is instantiated.

    The Builder class handles all build orchestration including:
        - Temporary directory creation and cleanup
        - Artifact collection and validation
        - Platform-specific artifact naming
        - Moving artifacts to the final output directory
        - Automatic discovery across dependent packages

    Subclasses must implement:
        create_artifacts: Create artifacts in the provided temporary directory.

    Class Attributes:
        ARTIFACTS_DIR_NAME: Name of the output directory for built artifacts.
            Default is "dist". Can be overridden in subclasses.

    Build Lifecycle:
        1. Builder is instantiated (e.g., `MyBuilder()`)
        2. `__init__` calls `build()` automatically
        3. `build()` creates temporary directory
        4. `create_artifacts()` is invoked (subclass implementation)
        5. Artifacts are collected from temporary directory
        6. `rename_artifacts()` adds platform suffixes and moves to output
        7. Temporary directory is automatically cleaned up

    Discovery Mechanism:
        The `get_non_abstract_subclasses()` method uses pyrig's multi-package
        architecture to find all Builder subclasses across packages that depend
        on pyrig. This enables automatic discovery and execution of all builders
        when running `pyrig build`.

    Example:
        Basic builder implementation::

            from pathlib import Path
            from pyrig.dev.builders.base.base import Builder

            class MyBuilder(Builder):
                '''Custom artifact builder.'''

                @classmethod
                def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
                    '''Create custom artifacts.'''
                    artifact = temp_artifacts_dir / "my-artifact.tar.gz"
                    # Create your artifact
                    artifact.write_bytes(b"artifact content")

        Instantiate to trigger build::

            MyBuilder()  # Automatically builds and outputs to dist/

        Or use the build command::

            $ uv run pyrig build

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

        This is the core method that subclasses must implement to define their
        specific build logic. All artifacts should be written to the provided
        temporary directory. After this method completes, the Builder framework
        will automatically collect, rename, and move the artifacts to the final
        output directory.

        The temporary directory is guaranteed to exist and will be automatically
        cleaned up after the build completes, regardless of success or failure.

        Args:
            temp_artifacts_dir: Path to a temporary directory where artifacts
                should be created. This directory is empty when the method is
                called. All files created in this directory will be treated as
                artifacts and moved to the final output directory with
                platform-specific naming.

        Raises:
            Any exceptions raised by this method will propagate and cause the
            build to fail. The temporary directory will still be cleaned up.

        Example:
            ::

                @classmethod
                def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
                    '''Create a documentation archive.'''
                    output = temp_artifacts_dir / "docs.zip"
                    # Create your artifact
                    output.write_text("documentation")

        Note:
            This method is called automatically by the `build()` method. You
            should not call it directly.
        """

    def __init__(self) -> None:
        """Initialize the builder and trigger the build process.

        Instantiating a Builder subclass automatically triggers the build
        process by calling the class's `build()` method. This design allows
        builders to be invoked simply by instantiating them.

        The build process runs synchronously and completes before this
        constructor returns.

        Example:
            ::

                # Instantiation triggers the build
                MyBuilder()

                # Artifacts are now in dist/ directory

        Note:
            This method should not be overridden in subclasses. Override
            `create_artifacts()` instead to customize build behavior.
        """
        self.__class__.build()

    @classmethod
    def get_artifacts_dir(cls) -> Path:
        """Get the final output directory for artifacts.

        Returns the path to the directory where built artifacts will be placed
        after the build completes. This directory is created automatically if
        it doesn't exist.

        Returns:
            Path object pointing to the artifacts output directory. Default is
            "dist" relative to the current working directory, but can be
            customized by overriding the `ARTIFACTS_DIR_NAME` class attribute.

        Example:
            ::

                # Default behavior
                artifacts_dir = MyBuilder.get_artifacts_dir()
                # Returns: Path("dist")

                # Custom output directory
                class MyBuilder(Builder):
                    ARTIFACTS_DIR_NAME = "build/output"

                artifacts_dir = MyBuilder.get_artifacts_dir()
                # Returns: Path("build/output")
        """
        return Path(cls.ARTIFACTS_DIR_NAME)

    @classmethod
    def build(cls) -> None:
        """Execute the complete build process.

        This is the main orchestration method that manages the entire build
        lifecycle. It creates a temporary directory, invokes the subclass's
        `create_artifacts` method, collects the created artifacts, renames
        them with platform-specific suffixes, and moves them to the final
        output directory.

        The build process is atomic in the sense that artifacts are only moved
        to the final output directory after successful creation. The temporary
        directory is automatically cleaned up regardless of success or failure.

        Build Steps:
            1. Create temporary build directory
            2. Create artifacts subdirectory within temp directory
            3. Call `create_artifacts()` to generate artifacts
            4. Collect all files from the artifacts subdirectory
            5. Rename and move artifacts to final output directory
            6. Clean up temporary directory (automatic via context manager)

        Raises:
            FileNotFoundError: If `create_artifacts` doesn't create any files.
            Any exceptions raised by `create_artifacts` will propagate.

        Example:
            ::

                # Typically called automatically via __init__
                MyBuilder()

                # Can also be called directly
                MyBuilder.build()

        Note:
            This method is called automatically by `__init__`. You typically
            don't need to call it directly unless you want to trigger a build
            without instantiating the builder.

        See Also:
            create_artifacts: Subclass-implemented method that creates artifacts
            rename_artifacts: Adds platform suffixes and moves to output
            get_temp_artifacts: Collects artifacts from temporary directory
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

        Takes artifacts from the temporary build directory, renames them with
        platform-specific suffixes, and moves them to the final output directory.
        The output directory is created if it doesn't exist.

        Platform suffixes are determined by `platform.system()`:
            - Linux: `-Linux`
            - Windows: `-Windows`
            - macOS: `-Darwin`

        Args:
            artifacts: List of Path objects pointing to artifact files in the
                temporary directory. Each artifact will be renamed and moved.

        Example:
            If an artifact is named `myapp` and the platform is Linux::

                # Original: /tmp/xyz/dist/myapp
                # Final:    dist/myapp-Linux

            If an artifact is named `docs.zip` on Windows::

                # Original: /tmp/xyz/dist/docs.zip
                # Final:    dist/docs-Windows.zip

        Note:
            This method is called automatically by `build()` after
            `create_artifacts()` completes. The platform suffix is inserted
            before the file extension if one exists.
        """
        artifacts_dir = cls.get_artifacts_dir()
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        for artifact in artifacts:
            # rename the files with -platform.system()
            new_name = f"{artifact.stem}-{platform.system()}{artifact.suffix}"
            new_path = artifacts_dir / new_name
            logger.debug("Moving artifact: %s to: %s", artifact, new_path)
            shutil.move(str(artifact), str(new_path))
            logger.info("Created artifact: %s", new_path.name)

    @classmethod
    def get_temp_artifacts(cls, temp_artifacts_dir: Path) -> list[Path]:
        """Get all artifacts from the temporary build directory.

        Collects all files created in the temporary artifacts directory by
        the `create_artifacts` method. This is used to validate that the
        build process created at least one artifact.

        Args:
            temp_artifacts_dir: Path to the temporary artifacts directory
                where `create_artifacts` wrote its output files.

        Returns:
            List of Path objects for all files in the temporary artifacts
            directory. Only direct children are included (not recursive).

        Raises:
            FileNotFoundError: If the temporary artifacts directory is empty,
                indicating that `create_artifacts` didn't produce any output.

        Example:
            ::

                # After create_artifacts runs
                artifacts = cls.get_temp_artifacts(temp_dir)
                # Returns: [Path('/tmp/xyz/dist/myapp'), Path('/tmp/xyz/dist/docs.zip')]

        Note:
            This method is called automatically by `build()` after
            `create_artifacts()` completes. It validates that at least one
            artifact was created.
        """
        paths = list(temp_artifacts_dir.glob("*"))
        if not paths:
            msg = f"Expected {temp_artifacts_dir} to contain files"
            raise FileNotFoundError(msg)
        return paths

    @classmethod
    def get_artifacts(cls) -> list[Path]:
        """Get all artifacts from the final output directory.

        Retrieves all artifact files that have been built and moved to the
        final output directory. This is useful for inspecting or processing
        artifacts after the build completes.

        Returns:
            List of Path objects for all files in the artifacts output
            directory. Returns an empty list if the directory doesn't exist
            or contains no files.

        Example:
            ::

                # After building
                MyBuilder()

                # Get all built artifacts
                artifacts = MyBuilder.get_artifacts()
                # Returns: [Path('dist/myapp-Linux'), Path('dist/docs-Linux.zip')]

        Note:
            This returns artifacts from the final output directory (e.g., `dist/`),
            not the temporary build directory. Artifacts will have platform-specific
            suffixes added by `rename_artifacts()`.
        """
        return list(cls.get_artifacts_dir().glob("*"))

    @classmethod
    def get_temp_artifacts_path(cls, temp_dir: Path) -> Path:
        """Create and return the temporary artifacts subdirectory.

        Creates a subdirectory within the temporary build directory where
        artifacts will be created. The subdirectory name matches the final
        output directory name (e.g., "dist").

        Args:
            temp_dir: Path to the parent temporary directory created by the
                build process.

        Returns:
            Path to the created artifacts subdirectory. The directory is
            guaranteed to exist when this method returns.

        Example:
            ::

                with tempfile.TemporaryDirectory() as temp_dir:
                    artifacts_path = cls.get_temp_artifacts_path(Path(temp_dir))
                    # Returns: Path('/tmp/xyz/dist')
                    # Directory is created and ready for use

        Note:
            This method is called automatically by `build()`. The created
            directory is passed to `create_artifacts()` as the location where
            artifacts should be written.
        """
        path = temp_dir / cls.ARTIFACTS_DIR_NAME
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_non_abstract_subclasses(cls) -> list[type["Builder"]]:
        """Discover all non-abstract Builder subclasses across dependent packages.

        Uses pyrig's multi-package architecture to find all concrete Builder
        subclasses across all packages that depend on pyrig. This enables
        automatic discovery of builders defined in any package in the
        dependency chain.

        The discovery process:
            1. Finds all packages that depend on pyrig
            2. Looks for `dev.builders` modules in each package
            3. Discovers all Builder subclasses in those modules
            4. Filters to only non-abstract classes
            5. Discards parent classes, keeping only leaf implementations

        Returns:
            List of Builder subclass types (not instances). Only concrete
            (non-abstract) leaf classes are included. Parent classes in
            inheritance hierarchies are excluded.

        Example:
            ::

                # Discover all builders
                builder_classes = Builder.get_non_abstract_subclasses()
                # Returns: [MyAppBuilder, DocumentationBuilder, ...]

                # Instantiate each to trigger builds
                for builder_cls in builder_classes:
                    builder_cls()

        Note:
            This method is used by `init_all_non_abstract_subclasses()` to
            implement the `pyrig build` command. It leverages the dependency
            graph to find builders across the entire package ecosystem.

        See Also:
            init_all_non_abstract_subclasses: Instantiates all discovered builders
            pyrig.src.modules.package.get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep:
                Core discovery mechanism
        """
        return get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep(
            cls,
            pyrig,
            builders,
            discard_parents=True,
        )

    @classmethod
    def init_all_non_abstract_subclasses(cls) -> None:
        """Instantiate all discovered Builder subclasses to trigger builds.

        Discovers all non-abstract Builder subclasses across all packages
        depending on pyrig and instantiates each one. Since instantiation
        triggers the build process (via `__init__`), this effectively builds
        all artifacts for all discovered builders.

        This is the implementation of the `pyrig build` command. It enables
        building all artifacts with a single command, regardless of how many
        builders are defined across how many packages.

        Build Process:
            1. Call `get_non_abstract_subclasses()` to discover builders
            2. Instantiate each builder class
            3. Each instantiation triggers that builder's build process
            4. All artifacts are created in their respective output directories

        Example:
            ::

                # Build all artifacts
                Builder.init_all_non_abstract_subclasses()

                # This discovers and builds:
                # - MyAppBuilder -> dist/myapp-Linux
                # - DocumentationBuilder -> dist/docs-Linux.zip
                # - Any other builders in dependent packages

        Note:
            This method is called by the `pyrig build` command. Builders are
            instantiated sequentially, not in parallel. Each builder completes
            before the next one starts.

        See Also:
            get_non_abstract_subclasses: Discovery mechanism for finding builders
            pyrig.dev.cli.commands.build_artifacts.build_artifacts: Build command
        """
        builders = cls.get_non_abstract_subclasses()
        for builder_cls in builders:
            builder_cls()

    @classmethod
    def get_app_name(cls) -> str:
        """Get the application name from pyproject.toml.

        Reads the project name from the `[project]` section of pyproject.toml.
        This is typically used for naming artifacts and executables.

        Returns:
            The project name as a string (e.g., "myapp", "pyrig").

        Example:
            ::

                # If pyproject.toml contains:
                # [project]
                # name = "myapp"

                name = MyBuilder.get_app_name()
                # Returns: "myapp"

        See Also:
            pyrig.dev.configs.pyproject.PyprojectConfigFile.get_project_name:
                Implementation that reads from pyproject.toml
        """
        return PyprojectConfigFile.get_project_name()

    @classmethod
    def get_root_path(cls) -> Path:
        """Get the project root directory path.

        Returns the absolute path to the project root directory, which is the
        parent directory of the source package. This is typically the directory
        containing pyproject.toml.

        Returns:
            Absolute Path to the project root directory.

        Example:
            ::

                root = MyBuilder.get_root_path()
                # Returns: Path('/home/user/myproject')

        Note:
            This is calculated by finding the source package directory and
            getting its parent. The source package is determined by the
            package name in pyproject.toml.
        """
        src_pkg = get_src_package()
        src_path = ModulePath.pkg_type_to_dir_path(src_pkg)
        return src_path.parent

    @classmethod
    def get_main_path(cls) -> Path:
        """Get the absolute path to the main.py entry point.

        Returns the absolute path to the main.py file in the source package.
        This is the entry point file that PyInstaller and other builders use
        to create executables.

        Returns:
            Absolute Path to the main.py file.

        Example:
            ::

                main_path = MyBuilder.get_main_path()
                # Returns: Path('/home/user/myproject/myapp/main.py')

        Note:
            This combines the source package path with the relative path to
            main.py within the package structure.

        See Also:
            get_main_path_from_src_pkg: Gets the relative path to main.py
        """
        return cls.get_src_pkg_path() / cls.get_main_path_from_src_pkg()

    @classmethod
    def get_resources_path(cls) -> Path:
        """Get the absolute path to the resources directory.

        Returns the absolute path to the resources directory in the source
        package. This directory contains static files like images, configs,
        and templates that need to be bundled with the application.

        Returns:
            Absolute Path to the resources directory.

        Example:
            ::

                resources_path = MyBuilder.get_resources_path()
                # Returns: Path('/home/user/myproject/myapp/resources')

        Note:
            This combines the source package path with the relative path to
            the resources directory within the package structure.

        See Also:
            get_resources_path_from_src_pkg: Gets the relative path to resources
        """
        return cls.get_src_pkg_path() / cls.get_resources_path_from_src_pkg()

    @classmethod
    def get_src_pkg_path(cls) -> Path:
        """Get the absolute path to the source package.

        Returns the absolute path to the main source package directory. This
        is the top-level package containing the application code.

        Returns:
            Absolute Path to the source package directory.

        Example:
            ::

                src_path = MyBuilder.get_src_pkg_path()
                # Returns: Path('/home/user/myproject/myapp')

        Note:
            This combines the project root path with the package name from
            pyproject.toml.
        """
        return cls.get_root_path() / PyprojectConfigFile.get_package_name()

    @classmethod
    def get_main_path_from_src_pkg(cls) -> Path:
        """Get the relative path to main.py from the source package.

        Calculates the relative path from the source package root to the
        main.py entry point file. This is used to construct the absolute
        path to main.py.

        Returns:
            Relative Path from source package to main.py (e.g., Path("main.py")).

        Example:
            ::

                rel_path = MyBuilder.get_main_path_from_src_pkg()
                # Returns: Path('main.py')

        Note:
            This uses pyrig's module path utilities to calculate the relative
            path based on the module structure. The path is relative to the
            source package, not the project root.
        """
        project_main_file = ModulePath.module_name_to_relative_file_path(main.__name__)
        pyrig_pkg_dir = ModulePath.pkg_name_to_relative_dir_path(pyrig.__name__)
        return project_main_file.relative_to(pyrig_pkg_dir)

    @classmethod
    def get_resources_path_from_src_pkg(cls) -> Path:
        """Get the relative path to resources from the source package.

        Calculates the relative path from the source package root to the
        resources directory. This is used to construct the absolute path
        to the resources directory.

        Returns:
            Relative Path from source package to resources directory
            (e.g., Path("resources")).

        Example:
            ::

                rel_path = MyBuilder.get_resources_path_from_src_pkg()
                # Returns: Path('resources')

        Note:
            This uses pyrig's module path utilities to calculate the relative
            path based on the module structure. The path is relative to the
            source package, not the project root.
        """
        resources_path = ModulePath.pkg_name_to_relative_dir_path(resources.__name__)
        pyrig_pkg_dir = ModulePath.pkg_name_to_relative_dir_path(pyrig.__name__)
        return resources_path.relative_to(pyrig_pkg_dir)
