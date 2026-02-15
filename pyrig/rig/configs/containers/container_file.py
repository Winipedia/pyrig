"""Manage Containerfile configuration.

Generate Docker-compatible Containerfile with best practices: Python slim
base, uv package manager, non-root user (appuser), optimized layer caching, and
proper permissions. Compatible with Docker, Podman, and OCI-compliant runtimes.

See Also:
    Containerfile spec: https://github.com/containers/common/blob/main/docs/Containerfile.5.md
"""

import json
from pathlib import Path

from pyrig.main import main
from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.package_manager import PackageManager


class ContainerfileConfigFile(StringConfigFile):
    """Manage Containerfile generation.

    Produce production-ready Containerfile with Python slim base, uv package
    manager, non-root user (appuser, UID 1000), optimized layer caching, and
    configurable entrypoint. Compatible with Docker, Podman, and buildah.

    Example:
        >>> ContainerfileConfigFile.I.validate()

    See Also:
        `pyrig.rig.configs.pyproject.PyprojectConfigFile`
        `pyrig.rig.tools.package_manager.PackageManager`
    """

    def filename(self) -> str:
        """Return 'Containerfile'."""
        return "Containerfile"

    def parent_path(self) -> Path:
    def parent_path(self) -> Path:
        Returns:
            Filename without extension or path.
        """Return project root."""
        return Path()

    def extension(self) -> str:
        """Return empty string (no extension)."""
        return ""

    def extension_separator(self) -> str:

        Returns:
            File extension without separator.
        """Return empty string (no separator)."""
        return ""

    def lines(self) -> list[str]:
        """Return Containerfile build instructions via `layers()`."""
        return self.layers()

    def layers(self) -> list[str]:

        Returns:
            List of file content lines.
        """Generate Containerfile build instructions.

        Builds optimized layer sequence: base image, workdir, uv install,
        dependency copy (for caching), user creation, source copy, dependency
        install, cleanup, entrypoint/command.

        Returns:
            Containerfile instructions (FROM, WORKDIR, COPY, RUN, etc.).

        Note:
            Reads from `pyproject.toml` and may make API calls to resolve the
            Python version.
        """
        latest_python_version = PyprojectConfigFile.I.latest_possible_python_version()
        project_name = PyprojectConfigFile.I.project_name()
        package_name = PyprojectConfigFile.I.package_name()
        app_user_name = "appuser"
        entrypoint_args = list(PackageManager.I.run_args(project_name))
        default_cmd_args = [main.__name__]
        return [
            f"FROM python:{latest_python_version}-slim",
            f"WORKDIR /{project_name}",
            "COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv",
            "COPY README.md LICENSE pyproject.toml uv.lock ./",
            f"RUN useradd -m -u 1000 {app_user_name}",
            f"RUN chown -R {app_user_name}:{app_user_name} .",
            f"USER {app_user_name}",
            f"COPY --chown=appuser:appuser {package_name} {package_name}",
            "RUN uv sync --no-group dev",
            "RUN rm README.md LICENSE pyproject.toml uv.lock",
            f"ENTRYPOINT {json.dumps(entrypoint_args)}",
            # if the image is provided a different command, it will run that instead
            # so adding a default is convenient without restricting usage
            f"CMD {json.dumps(default_cmd_args)}",
        ]
