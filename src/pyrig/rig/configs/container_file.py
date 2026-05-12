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
        (project metadata and lock file) are copied before the source tree is
        added. This maximizes Docker/Podman build cache reuse when only source
        code changes.

        Returns:
            List of Containerfile instruction strings followed by a trailing
            empty string.

        Note:
            Reads ``requires-python`` from ``pyproject.toml`` and falls back to
            the bundled ``LATEST_PYTHON_VERSION`` resource file when no upper
            bound is specified.
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
            f"COPY --chown={app_user_name}:{app_user_name} {package_root} {package_root}",  # noqa: E501
            f"RUN {install_dependencies_no_dev}",
            f"RUN rm {copy_files}",
            f"ENTRYPOINT {entrypoint}",
            "",
        ]
