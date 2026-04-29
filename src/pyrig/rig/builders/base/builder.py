"""Abstract base class for artifact builders.

Provides `BuilderConfigFile`, the base class for all artifact generators in the
pyrig framework. Builders produce platform-specific outputs such as executables,
documentation archives, and packages.
"""

import logging
import platform
import shutil
import tempfile
from abc import abstractmethod
from collections.abc import Generator, Iterable
from pathlib import Path
from types import ModuleType

import typer

from pyrig.rig import builders
from pyrig.rig.configs.base.config_file import ListConfigFile
from pyrig.rig.tools.package_manager import PackageManager

logger = logging.getLogger(__name__)


class BuilderConfigFile(ListConfigFile):
    """Abstract base class for artifact builders.

    Extends `ListConfigFile` but repurposes its interface for build operations
    rather than configuration file management:

    - ``load()`` returns existing artifacts found in the output directory.
    - ``dump()`` triggers the full build process.
    - ``validate()`` runs the build if no artifacts are present yet.
    - ``is_correct()`` returns ``True`` if at least one artifact exists.
    - ``create_file()`` creates the output directory.

    Build lifecycle (managed by ``build()``):

    1. A temporary directory is created via ``tempfile.TemporaryDirectory``.
    2. ``create_artifacts()`` is called with a subdirectory inside that temp dir.
    3. All files in the temp subdirectory are collected.
    4. Each file is renamed with a platform suffix (e.g., ``app-Linux.zip``)
       and moved to the final output directory (default: ``dist/``).
    5. The temporary directory and its contents are deleted automatically.

    Subclasses must implement ``create_artifacts()`` to define their build logic.

    Example:
        Basic builder subclass::

            class ExecutableBuilder(BuilderConfigFile):

                def create_artifacts(self, temp_artifacts_dir: Path) -> None:
                    exe_path = temp_artifacts_dir / f"{self.app_name()}.exe"
                    # compile and write the executable to exe_path
    """

    @abstractmethod
    def create_artifacts(self, temp_artifacts_dir: Path) -> None:
        """Create build artifacts in the provided temporary directory.

        This is the sole method subclasses must implement. Write all output
        files directly into ``temp_artifacts_dir``. After this method returns,
        ``build()`` will collect every file in that directory, append a
        platform suffix to each filename, and move them to the final output
        directory.

        Args:
            temp_artifacts_dir: Directory where artifacts must be written.
                Every file placed here is treated as a build artifact and
                processed by the framework automatically.

        Example:
            ::

                def create_artifacts(self, temp_artifacts_dir: Path) -> None:
                    output = temp_artifacts_dir / "docs.zip"
                    output.write_bytes(archive_bytes)
        """

    @classmethod
    def definition_package(cls) -> ModuleType:
        """Return the package where builder subclass definitions are discovered.

        Overrides the parent default of ``pyrig.rig.configs`` so that builder
        subclass discovery targets ``pyrig.rig.builders`` instead.

        Returns:
            The ``pyrig.rig.builders`` module.
        """
        return builders

    @classmethod
    def dist_dir_name(cls) -> str:
        """Return the name of the artifacts output directory.

        Defaults to ``"dist"``. Subclasses can override to change the output
        location. Implemented as a classmethod because it is referenced by
        ``WorkflowConfigFile`` subclasses, which need the name without
        instantiating an abstract builder.

        Returns:
            Directory name where finished artifacts are placed (e.g., ``"dist"``).
        """
        return "dist"

    @classmethod
    def dist_dir_path(cls) -> Path:
        """Return the path to the artifacts output directory.

        Wraps ``dist_dir_name()`` in a ``Path`` object. The resulting path is
        relative to the current working directory.
        Implemented as a classmethod because it is referenced by ``WorkflowConfigFile``
        subclasses, which need the path without instantiating an abstract builder.

        Returns:
            Relative path to the artifacts output directory (e.g., ``Path("dist")``).
        """
        return Path(cls.dist_dir_name())

    def parent_path(self) -> Path:
        """Return the output directory path for artifacts.

        Returns:
            ``Path`` to the artifacts directory, derived from ``dist_dir_name()``.
        """
        return self.dist_dir_path()

    def stem(self) -> str:
        """Return an empty string.

        Builders do not produce a single named file, so no stem is needed.
        """
        return ""

    def extension(self) -> str:
        """Return an empty string.

        Builders do not produce a single file with a fixed extension.
        """
        return ""

    def _configs(self) -> list[Path]:
        """Return an empty list.

        Builders have no expected configuration structure; the build output
        is determined entirely by ``create_artifacts()``.
        """
        return []

    def _load(self) -> list[Path]:
        """List all artifacts currently present in the output directory.

        Returns:
            All files (non-recursive) found directly inside ``parent_path()``.
            Returns an empty list if the directory does not exist or is empty.
        """
        return list(self.parent_path().glob("*"))

    def _dump(self, configs: list[Path]) -> None:  # noqa: ARG002
        """Trigger the build process.

        The ``configs`` parameter is required by the parent class interface but
        is not used here; the build is fully driven by ``create_artifacts()``.

        Args:
            configs: Ignored.
        """
        self.build()

    def is_correct(self) -> bool:
        """Return ``True`` if at least one artifact exists in the output directory.

        Used by the parent ``validate()`` lifecycle to decide whether a build
        is needed. A builder is considered correct when its output directory
        contains at least one artifact.

        Returns:
            ``True`` if ``load()`` returns a non-empty list, ``False`` otherwise.
        """
        return bool(self.load())

    def create_file(self) -> None:
        """Create the output directory for artifacts.

        Creates ``parent_path()`` (and any missing parent directories). The
        actual artifact files are produced later by ``create_artifacts()``.
        """
        self.parent_path().mkdir(parents=True, exist_ok=True)

    def build(self) -> None:
        """Run the full build pipeline.

        Orchestrates the entire build lifecycle:

        1. Creates a temporary directory.
        2. Calls ``temp_artifacts_path()`` to create a ``dist/`` subdirectory
           inside it.
        3. Calls ``create_artifacts()`` with that subdirectory.
        4. Collects all files written there via ``temp_artifacts()``.
        5. Calls ``rename_artifacts()`` to add platform suffixes and move
           each file to the final output directory.

        The temporary directory is cleaned up automatically when the context
        manager exits, regardless of whether the build succeeds or fails.
        """
        logger.debug("Building artifacts with %s", self.__class__.__name__)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_artifacts_dir = self.temp_artifacts_path(temp_dir_path)
            self.create_artifacts(temp_artifacts_dir)
            artifacts = self.temp_artifacts(temp_artifacts_dir)
            self.rename_artifacts(artifacts)

    def rename_artifacts(self, artifacts: Iterable[Path]) -> None:
        """Move each artifact to the output directory with a platform-specific name.

        Iterates over the provided artifact paths and delegates each one to
        ``rename_artifact()``.

        Args:
            artifacts: Artifact paths from the temporary build directory.
        """
        for artifact in artifacts:
            self.rename_artifact(artifact)

    def rename_artifact(self, artifact: Path) -> None:
        """Move a single artifact to the output directory with a platform suffix.

        Computes the platform-specific destination path via
        ``platform_specific_path()``, creates any missing parent directories,
        moves the file from the temporary location, and prints the destination
        path to the console.

        Args:
            artifact: Path to the artifact file in the temporary build directory.
        """
        platform_specific_path = self.platform_specific_path(artifact)
        logger.debug(
            "Moving artifact: %s to: %s",
            artifact,
            platform_specific_path,
        )
        # create the platform-specific path's parent directory if it doesn't exist
        platform_specific_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(artifact, platform_specific_path)
        typer.echo(f"Created {platform_specific_path}")

    def platform_specific_path(self, artifact: Path) -> Path:
        """Return the final output path for an artifact, including the platform suffix.

        Combines ``parent_path()`` with the result of
        ``platform_specific_name()`` to produce the full destination path.

        Args:
            artifact: Artifact path (typically from the temporary directory).

        Returns:
            Destination path inside the output directory with the platform
            suffix applied to the filename.
        """
        return self.parent_path() / self.platform_specific_name(artifact)

    def platform_specific_name(self, artifact: Path) -> str:
        """Return the artifact filename with the current platform appended as a suffix.

        Produces names of the form ``<stem>-<platform><ext>``, for example
        ``myapp-Linux.exe`` or ``docs-Darwin.zip``. The platform string is
        determined by ``platform.system()``.

        Args:
            artifact: Artifact path whose name will be transformed.

        Returns:
            Filename string with the platform suffix inserted before the
            extension (e.g., ``"myapp-Linux.exe"``).
        """
        return f"{artifact.stem}-{platform.system()}{artifact.suffix}"

    def temp_artifacts(self, temp_artifacts_dir: Path) -> Generator[Path, None, None]:
        """Yield all files in the temporary artifacts directory.

        Args:
            temp_artifacts_dir: Directory populated by ``create_artifacts()``.

        Returns:
            Generator of artifact paths (non-recursive). Yields nothing if no
            files were written during the build.
        """
        return temp_artifacts_dir.glob("*")

    def temp_artifacts_path(self, temp_dir: Path) -> Path:
        """Create and return the build subdirectory inside the temporary directory.

        Creates a subdirectory named after ``dist_dir_name()`` inside
        ``temp_dir``. This is the directory passed to ``create_artifacts()``.

        Args:
            temp_dir: Root of the temporary directory created by ``build()``.

        Returns:
            Path to the newly created subdirectory.
        """
        path = temp_dir / self.dist_dir_path()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def app_name(self) -> str:
        """Return the project name defined in ``pyproject.toml``.

        Convenience helper for subclasses that need the project name when
        constructing artifact filenames inside ``create_artifacts()``.
        """
        return PackageManager.I.project_name()
