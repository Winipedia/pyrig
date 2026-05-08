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
from pathlib import Path
from types import ModuleType

import typer

from pyrig.rig import builders
from pyrig.rig.configs.base.config_file import ListConfigFile

logger = logging.getLogger(__name__)


class BuilderConfigFile(ListConfigFile):
    """Abstract base class for artifact builders.

    Extends `ListConfigFile` but repurposes its interface for build operations
    rather than configuration file management:

    - ``load()`` returns a list containing the artifact path if it exists on disk.
    - ``dump()`` triggers the full build process.
    - ``validate()`` runs the build if the artifact is not present yet.
    - ``create_file()`` creates the output directory.

    Each builder produces a single artifact whose filename is composed of
    ``non_platform_stem()`` plus a platform suffix (from ``platform.system()``)
    plus ``extension()``, e.g. ``myapp-Linux`` or ``docs-Darwin.zip``.

    Build lifecycle (managed by ``build()``):

    1. A temporary directory is created via ``tempfile.TemporaryDirectory``.
    2. ``create_artifact()`` is called with that temporary directory and is
       expected to write a file named ``filename()`` into it.
    3. ``move_artifact()`` moves that file to the final output directory
       (default: ``dist/``).
    4. The temporary directory and its contents are deleted automatically.

    Subclasses must implement ``non_platform_stem()`` and ``create_artifact()``
    to define their build logic.

    Example:
        Basic builder subclass::

            class ExecutableBuilder(BuilderConfigFile):

                def non_platform_stem(self) -> str:
                    return "myapp"

                def extension(self) -> str:
                    return "exe"

                def create_artifact(self, tmp_path: Path) -> None:
                    exe_path = tmp_path / self.filename()
                    # compile and write the executable to exe_path
    """

    @abstractmethod
    def non_platform_stem(self) -> str:
        """Return the stem without a platform suffix.

        This is the base name of the artifact before the platform suffix is
        appended. For example, if the final artifact is named
        ``myapp-Linux.zip``, this method should return ``myapp``.

        Returns:
            Base stem string without the platform suffix (e.g., ``"myapp"``).
        """

    @abstractmethod
    def create_artifact(self, tmp_path: Path) -> None:
        """Create the build artifact in the provided temporary directory.

        Subclasses must write a single file into ``tmp_path`` named exactly
        ``self.filename()`` (i.e., ``"<stem><extension_separator><extension>"``
        with the platform-suffixed stem). After this method returns, ``build()``
        moves that file to the final output directory.

        Args:
            tmp_path: Directory where the artifact must be written. The file
                placed at ``tmp_path / self.filename()`` is moved to
                ``parent_path()`` by the framework.

        Example:
            ::

                def create_artifact(self, tmp_path: Path) -> None:
                    output = tmp_path / self.filename()
                    output.write_bytes(archive_bytes)
        """

    @classmethod
    def dependency_package(cls) -> ModuleType:
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

    def stem(self) -> str:
        """Return the stem for the artifact filename.

        Combines ``non_platform_stem()`` with the current ``platform.system()``
        value, producing names like ``myapp-Linux`` or ``docs-Darwin``.
        """
        return f"{self.non_platform_stem()}-{platform.system()}"

    def parent_path(self) -> Path:
        """Return the output directory path for artifacts.

        Returns:
            ``Path`` to the artifacts directory, derived from ``dist_dir_name()``.
        """
        return self.dist_dir_path()

    def _configs(self) -> list[Path]:
        """Return the expected artifact path.

        The required "configuration" of a builder is simply the existence of
        its single artifact at ``path()``. ``is_correct()`` (inherited from
        ``ConfigFile``) compares ``configs()`` against ``load()``.
        """
        return [self.path()]

    def _load(self) -> list[Path]:
        """Return the artifact path if it currently exists on disk.

        Returns:
            ``[self.path()]`` if the artifact file exists, otherwise an empty
            list.
        """
        return [self.path()] if self.path().exists() else []

    def _dump(self, configs: list[Path]) -> None:  # noqa: ARG002
        """Trigger the build process.

        The ``configs`` parameter is required by the parent class interface but
        is not used here; the build is fully driven by ``build()``.

        Args:
            configs: Ignored.
        """
        self.build()

    def create_file(self) -> None:
        """Create the output directory for artifacts.

        Creates ``parent_path()`` (and any missing parent directories). The
        actual artifact files are produced later by ``create_artifact()``.
        """
        self.parent_path().mkdir(parents=True, exist_ok=True)

    def build(self) -> None:
        """Run the full build pipeline.

        Orchestrates the entire build lifecycle:

        1. Creates a temporary directory.
        2. Calls ``create_artifact()`` with that directory; the subclass is
           expected to write a file named ``self.filename()`` there.
        3. Calls ``move_artifact()`` to move the file to ``parent_path()``.

        The temporary directory is cleaned up automatically when the context
        manager exits, regardless of whether the build succeeds or fails.
        """
        logger.debug("Building artifacts with %s", self.__class__.__name__)
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            self.create_artifact(tmp_path=tmp_path)
            self.move_artifact(tmp_path)

    def move_artifact(self, tmp_path: Path) -> None:
        """Move the artifact from the temp directory to the output directory.

        Reads the artifact at ``tmp_path / self.filename()`` (already named
        with the platform-suffixed stem produced by ``stem()``), moves it into
        ``parent_path()``, and prints the artifact path to the console.

        Args:
            tmp_path: Path to the temporary build directory passed to
                ``create_artifact()``.
        """
        artifact = tmp_path / self.filename()

        dist_path = self.parent_path()
        logger.debug(
            "Moving artifact: %s to: %s",
            artifact,
            dist_path,
        )
        shutil.move(artifact, dist_path)
        typer.echo(f"Created {self.path()}")
