"""Configuration management for Containerfile files.

Manages Docker-compatible Containerfile generation with best practices: Python slim
base, uv package manager, non-root user (appuser), optimized layer caching, and
proper permissions. Compatible with Docker, Podman, and OCI-compliant runtimes.

See Also:
    Containerfile spec: https://github.com/containers/common/blob/main/docs/Containerfile.5.md
"""

import json
from pathlib import Path

from pyrig.dev.configs.base.text import TextConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.management.package_manager import PackageManager
from pyrig.main import main


class ContainerfileConfigFile(TextConfigFile):
    """Containerfile configuration manager.

    Generates production-ready Containerfile with Python slim base, uv package
    manager, non-root user (appuser, UID 1000), optimized layer caching, and
    configurable entrypoint. Compatible with Docker, Podman, and buildah.

    Examples:
        Generate Containerfile::

            ContainerfileConfigFile()

        Build and run::

            docker build -t myproject .
            docker run myproject

    See Also:
        pyrig.dev.configs.pyproject.PyprojectConfigFile
        pyrig.src.management.package_manager.PackageManager
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the Containerfile filename.

        Returns:
            str: "Containerfile".
        """
        return "Containerfile"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for Containerfile.

        Returns:
            Path: Project root.
        """
        return Path()

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension for Containerfile.

        Returns:
            str: Empty string (no extension).
        """
        return ""

    @classmethod
    def get_extension_sep(cls) -> str:
        """Get the extension separator for Containerfile.

        Returns:
            str: Empty string (no separator).
        """
        return ""

    @classmethod
    def get_content_str(cls) -> str:
        """Get the complete Containerfile content.

        Returns:
            str: Complete Containerfile with all build instructions.

        Note:
            Reads from pyproject.toml and may make API calls for Python version.
        """
        return "\n\n".join(cls.get_layers())

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the Containerfile is valid and complete.

        Validates all expected layers are present.

        Returns:
            bool: True if all layers present, False otherwise.
        """
        all_layers_in_file = all(
            layer in cls.get_file_content() for layer in cls.get_layers()
        )
        return super().is_correct() or all_layers_in_file

    @classmethod
    def get_layers(cls) -> list[str]:
        """Get Containerfile build instructions.

        Generates optimized layer sequence: base image, workdir, uv install,
        dependency copy (for caching), user creation, source copy, dependency
        install, cleanup, entrypoint/command.

        Returns:
            list[str]: Containerfile instructions (FROM, WORKDIR, COPY, RUN, etc.).

        Note:
            Reads from pyproject.toml and may make API calls for Python version.
        """
        latest_python_version = PyprojectConfigFile.get_latest_possible_python_version()
        project_name = PyprojectConfigFile.get_project_name()
        package_name = PyprojectConfigFile.get_package_name()
        app_user_name = "appuser"
        entrypoint_args = list(PackageManager.L.get_run_args(project_name))
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
