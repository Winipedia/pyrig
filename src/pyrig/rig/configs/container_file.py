"""Containerfile configuration management."""

import json
from pathlib import Path

from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.markdown.readme import ReadmeConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.package_manager import PackageManager


class ContainerfileConfigFile(StringConfigFile):
    """Generates a production-ready Containerfile for the project.

    Produces a Containerfile with a Python slim base image, uv as the package
    manager, a non-root runtime user (appuser, UID 1000), and layer ordering
    optimized for cache reuse. Compatible with Docker, Podman, and buildah.

    Example:
        >>> ContainerfileConfigFile.I.validate()
    """

    def stem(self) -> str:
        """Return the filename stem 'Containerfile'."""
        return "Containerfile"

    def parent_path(self) -> Path:
        """Return the project root directory."""
        return Path()

    def extension(self) -> str:
        """Return an empty string (Containerfile has no file extension)."""
        return ""

    def extension_separator(self) -> str:
        """Return an empty string, overriding the base class default separator '.'.

        Prevents the base class from appending a dot to the filename, since
        Containerfile uses neither an extension nor a separator.
        """
        return ""

    def lines(self) -> list[str]:
        """Return the Containerfile build instructions.

        Returns:
            List of instruction lines produced by `layers()`.
        """
        return self.layers()

    def layers(self) -> list[str]:
        """Generate the complete sequence of Containerfile build instructions.

        Produces an optimized layer order so that infrequently changing files
        (project metadata and lock file) are copied and dependencies are
        installed before the source tree is added. This maximizes Docker/Podman
        build cache reuse when only source code changes.

        The generated layer sequence is:

        1. ``FROM python:{version}-slim`` — base image pinned to the highest
           Python version allowed by the project's ``requires-python`` constraint.
        2. ``WORKDIR /{project_name}`` — set the container working directory.
        3. ``COPY --from=ghcr.io/astral-sh/uv:latest`` — copy the uv binary
           directly from the official uv image.
        4. ``COPY {readme} {license} {pyproject.toml} {uv.lock} ./`` — copy
           metadata files needed for dependency installation.
        5. ``RUN useradd -m -u 1000 appuser`` — create the non-root runtime user.
        6. ``RUN chown -R appuser:appuser .`` — transfer ownership of the workdir.
        7. ``USER appuser`` — switch to the non-root user for all subsequent steps.
        8. ``COPY --chown=appuser:appuser {package_root} {package_root}`` — copy
           the package source tree with correct ownership.
        9. ``RUN uv sync --no-group dev`` — install production dependencies only.
        10. ``RUN rm {metadata_files}`` — remove metadata files to reduce image size.
        11. ``ENTRYPOINT ["uv", "run", "{project_name}"]`` — set the project CLI
            as the container entrypoint.

        Returns:
            List of Containerfile instruction strings followed by a trailing
            empty string.

        Note:
            Reads ``requires-python`` from ``pyproject.toml`` and may make an
            external API call to resolve the latest compatible Python version.
        """
        latest_python_version = PyprojectConfigFile.I.latest_possible_python_version()
        package_root = PackageManager.I.package_root().as_posix()
        project_name = PackageManager.I.project_name()
        workdir = Path(project_name).as_posix()
        app_user_name = "appuser"
        entrypoint = json.dumps(list(PackageManager.I.run_args(project_name)))
        readme_path, license_path, pyproject_path, lock_file_path = (
            ReadmeConfigFile.I.path().as_posix(),
            LicenseConfigFile.I.path().as_posix(),
            PyprojectConfigFile.I.path().as_posix(),
            PackageManager.I.lock_file().as_posix(),
        )
        copy_files = f"{readme_path} {license_path} {pyproject_path} {lock_file_path}"
        install_dependencies_no_dev = (
            PackageManager.I.install_dependencies_no_dev_args()
        )
        image_url, image_source_path, image_destination_path = (
            PackageManager.I.container_image()
        )

        return [
            f"FROM python:{latest_python_version}-slim",
            f"WORKDIR /{workdir}",
            f"COPY --from={image_url} {image_source_path} {image_destination_path}",
            f"COPY {copy_files} ./",
            f"RUN useradd -m -u 1000 {app_user_name}",
            f"RUN chown -R {app_user_name}:{app_user_name} .",
            f"USER {app_user_name}",
            f"COPY --chown=appuser:appuser {package_root} {package_root}",
            f"RUN {install_dependencies_no_dev}",
            f"RUN rm {copy_files}",
            f"ENTRYPOINT {entrypoint}",
            "",
        ]
