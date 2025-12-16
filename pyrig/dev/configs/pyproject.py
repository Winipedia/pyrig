"""Configuration management for pyproject.toml.

This module provides the PyprojectConfigFile class for managing the
project's pyproject.toml file. It handles project metadata, dependencies,
tool configurations (ruff, mypy, pytest, bandit), and build settings.

The configuration enforces pyrig's opinionated defaults:
    - All ruff rules enabled (with minimal exceptions)
    - Strict mypy type checking
    - Bandit security scanning
    - uv as the build backend
"""

import re
from functools import cache
from pathlib import Path
from subprocess import CompletedProcess  # nosec: B404
from typing import Any, Literal

import requests
from packaging.version import Version

from pyrig.dev.cli.commands.init_project import STANDARD_DEV_DEPS
from pyrig.dev.configs.base.base import TomlConfigFile
from pyrig.dev.utils.resources import return_resource_content_on_fetch_error
from pyrig.dev.utils.versions import VersionConstraint, adjust_version_to_level
from pyrig.src.git.git import get_repo_owner_and_name_from_git
from pyrig.src.modules.package import (
    get_pkg_name_from_cwd,
    get_pkg_name_from_project_name,
    get_project_name_from_cwd,
)
from pyrig.src.os.os import run_subprocess
from pyrig.src.testing.convention import (
    COVERAGE_THRESHOLD,
    TESTS_PACKAGE_NAME,
)


class PyprojectConfigFile(TomlConfigFile):
    """Configuration file manager for pyproject.toml.

    Manages the central project configuration including:
        - Project metadata (name, description, dependencies)
        - Build system configuration (uv)
        - Tool configurations (ruff, mypy, pytest, bandit)
        - CLI entry points

    The class provides utilities for querying project information
    and managing dependencies.
    """

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to pyproject.toml.

        Normalizes dependencies before writing.

        Args:
            config: The configuration dict to write.

        Raises:
            TypeError: If config is not a dict.
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to pyproject.toml file."
            raise TypeError(msg)
        # remove the versions from the dependencies
        cls.remove_wrong_dependencies(config)
        super().dump(config)

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the project root directory.

        Returns:
            Path to the project root.
        """
        return Path()

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the expected pyproject.toml configuration.

        Returns:
            Complete configuration dict with project metadata,
            dependencies, build system, and tool configurations.
        """
        from pyrig.dev.cli import (  # noqa: PLC0415
            cli,
        )

        repo_owner, _ = get_repo_owner_and_name_from_git(check_repo_url=False)

        return {
            "project": {
                "name": get_project_name_from_cwd(),
                "version": cls.get_project_version(),
                "description": cls.get_project_description(),
                "readme": "README.md",
                "authors": [
                    {"name": repo_owner},
                ],
                "license-files": ["LICENSE"],
                "requires-python": cls.get_project_requires_python(),
                "classifiers": [
                    *cls.make_python_version_classifiers(),
                ],
                "scripts": {
                    cls.get_project_name(): f"{cli.__name__}:{cli.main.__name__}"
                },
                "dependencies": cls.make_dependency_versions(cls.get_dependencies()),
            },
            "dependency-groups": {
                "dev": cls.make_dependency_versions(
                    cls.get_dev_dependencies(),
                    additional=cls.get_standard_dev_dependencies(),
                )
            },
            "build-system": {
                "requires": ["uv_build"],
                "build-backend": "uv_build",
            },
            "tool": {
                "uv": {
                    "build-backend": {
                        "module-name": get_pkg_name_from_cwd(),
                        "module-root": "",
                    }
                },
                "ruff": {
                    "exclude": [".*", "**/migrations/*.py"],
                    "lint": {
                        "select": ["ALL"],
                        "ignore": ["D203", "D213", "COM812", "ANN401"],
                        "fixable": ["ALL"],
                        "per-file-ignores": {
                            f"**/{TESTS_PACKAGE_NAME}/**/*.py": ["S101"],
                        },
                        "pydocstyle": {"convention": "google"},
                    },
                },
                "mypy": {
                    "strict": True,
                    "warn_unreachable": True,
                    "show_error_codes": True,
                    "files": ".",
                },
                "pytest": {
                    "ini_options": {
                        "testpaths": [TESTS_PACKAGE_NAME],
                        "addopts": f"--cov={cls.get_package_name()} --cov-report=term-missing --cov-fail-under={COVERAGE_THRESHOLD}",  # noqa: E501
                    }
                },
                "bandit": {
                    "exclude_dirs": [
                        ".*",
                    ],
                    "assert_used": {
                        "skips": [
                            f"*/{TESTS_PACKAGE_NAME}/*.py",
                        ],
                    },
                },
            },
        }

    @classmethod
    def remove_wrong_dependencies(cls, config: dict[str, Any]) -> None:
        """Normalize dependencies by removing version specifiers.

        Args:
            config: The configuration dict to modify in place.
        """
        # removes the versions from the dependencies
        config["project"]["dependencies"] = cls.make_dependency_versions(
            config["project"]["dependencies"]
        )
        config["dependency-groups"]["dev"] = cls.make_dependency_versions(
            config["dependency-groups"]["dev"]
        )

    @classmethod
    def get_project_description(cls) -> str:
        """Get the project description from pyproject.toml.

        Returns:
            The project description or empty string.
        """
        return str(cls.load().get("project", {}).get("description", ""))

    @classmethod
    def get_project_version(cls) -> str:
        """Get the project version from pyproject.toml.

        Returns:
            The project version or empty string.
        """
        return str(cls.load().get("project", {}).get("version", ""))

    @classmethod
    def make_python_version_classifiers(cls) -> list[str]:
        """Make the Python version classifiers.

        Returns:
            List of Python version classifiers.
        """
        versions = cls.get_supported_python_versions()
        return [
            f"Programming Language :: Python :: {v.major}.{v.minor}" for v in versions
        ]

    @classmethod
    def get_project_requires_python(cls, default: str = ">=3.12") -> str:
        """Get the project's requires-python from pyproject.toml.

        Returns:
            The project's requires-python or empty string.
        """
        return str(cls.load().get("project", {}).get("requires-python", default))

    @classmethod
    def make_dependency_versions(
        cls,
        dependencies: list[str],
        additional: list[str] | None = None,
    ) -> list[str]:
        """Normalize and merge dependency lists.

        Args:
            dependencies: Primary dependencies to process.
            additional: Additional dependencies to merge.

        Returns:
            Sorted, deduplicated list of normalized dependencies.
        """
        if additional is None:
            additional = []
        # remove all versions from the dependencies to compare them
        stripped_dependencies = {
            cls.remove_version_from_dep(dep) for dep in dependencies
        }
        additional = [
            dep
            for dep in additional
            if cls.remove_version_from_dep(dep) not in stripped_dependencies
        ]
        dependencies.extend(additional)
        return sorted(set(dependencies))

    @classmethod
    def remove_version_from_dep(cls, dep: str) -> str:
        """Strip version specifier from a dependency string.

        Args:
            dep: Dependency string like "requests>=2.0".

        Returns:
            Package name without version (e.g., "requests").
        """
        return re.split(r"[^a-zA-Z0-9_.-]", dep)[0]

    @classmethod
    def get_package_name(cls) -> str:
        """Get the Python package name (with underscores).

        Returns:
            The package name derived from the project name.
        """
        project_name = cls.get_project_name()
        return get_pkg_name_from_project_name(project_name)

    @classmethod
    def get_project_name(cls) -> str:
        """Get the project name from pyproject.toml.

        Returns:
            The project name or empty string.
        """
        return str(cls.load().get("project", {}).get("name", ""))

    @classmethod
    def get_all_dependencies(cls) -> list[str]:
        """Get all dependencies (runtime and dev).

        Returns:
            Combined list of all dependencies.
        """
        all_deps = cls.get_dependencies()
        all_deps.extend(cls.get_dev_dependencies())
        return all_deps

    @classmethod
    def get_standard_dev_dependencies(cls) -> list[str]:
        """Get pyrig's standard development dependencies.

        Returns:
            Sorted list of standard dev dependencies.
        """
        # sort the dependencies
        return sorted(STANDARD_DEV_DEPS)

    @classmethod
    def get_dev_dependencies(cls) -> list[str]:
        """Get development dependencies from pyproject.toml.

        Returns:
            List of dev dependencies.
        """
        dev_deps: list[str] = cls.load().get("dependency-groups", {}).get("dev", [])
        return dev_deps

    @classmethod
    def get_dependencies(cls) -> list[str]:
        """Get runtime dependencies from pyproject.toml.

        Returns:
            List of runtime dependencies.
        """
        deps: list[str] = cls.load().get("project", {}).get("dependencies", [])
        return deps

    @classmethod
    @return_resource_content_on_fetch_error(resource_name="LATEST_PYTHON_VERSION")
    @cache
    def fetch_latest_python_version(cls) -> str:
        """Fetch the latest stable Python version from endoflife.date.

        Returns:
            The latest stable Python version.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = "https://endoflife.date/api/python.json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data: list[dict[str, str]] = resp.json()
        # first element has metadata for latest stable
        return data[0]["latest"]

    @classmethod
    def get_latest_python_version(
        cls, level: Literal["major", "minor", "micro"] = "minor"
    ) -> Version:
        """Fetch the latest stable Python version from endoflife.date.

        Returns:
            The latest stable Python version as a string.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        latest_version = Version(cls.fetch_latest_python_version())
        return adjust_version_to_level(latest_version, level)

    @classmethod
    def get_latest_possible_python_version(
        cls, level: Literal["major", "minor", "micro"] = "micro"
    ) -> Version:
        """Get the latest Python version allowed by requires-python.

        Args:
            level: Version precision (major, minor, or micro).

        Returns:
            The latest allowed Python version.
        """
        constraint = cls.load()["project"]["requires-python"]
        version_constraint = VersionConstraint(constraint)
        version = version_constraint.get_upper_inclusive()
        if version is None:
            version = cls.get_latest_python_version()

        return adjust_version_to_level(version, level)

    @classmethod
    def get_first_supported_python_version(cls) -> Version:
        """Get the minimum supported Python version.

        Returns:
            The minimum Python version from requires-python.

        Raises:
            ValueError: If no lower bound is specified.
        """
        constraint = cls.get_project_requires_python()
        version_constraint = VersionConstraint(constraint)
        lower = version_constraint.get_lower_inclusive()
        if lower is None:
            msg = "Need a lower bound for python version"
            raise ValueError(msg)
        return lower

    @classmethod
    def get_supported_python_versions(cls) -> list[Version]:
        """Get all supported Python minor versions.

        Returns:
            List of supported Python versions (e.g., [3.10, 3.11, 3.12]).
        """
        constraint = cls.get_project_requires_python()
        version_constraint = VersionConstraint(constraint)
        return version_constraint.get_version_range(
            level="minor", upper_default=cls.get_latest_python_version()
        )

    @classmethod
    def update_dependencies(cls, *, check: bool = True) -> CompletedProcess[bytes]:
        """Update dependencies to their latest versions.

        Args:
            check: Whether to raise on non-zero exit code.

        Returns:
            The completed process result.
        """
        from pyrig.src.project.mgt import PROJECT_MGT  # noqa: PLC0415

        upgrade_deps = run_subprocess([PROJECT_MGT, "lock", "--upgrade"], check=check)
        _ = cls.install_dependencies(check=check)
        return upgrade_deps

    @classmethod
    def install_dependencies(cls, *, check: bool = True) -> CompletedProcess[bytes]:
        """Install project dependencies using uv sync.

        Args:
            check: Whether to raise on non-zero exit code.

        Returns:
            The completed process result.
        """
        from pyrig.src.project.mgt import PROJECT_MGT  # noqa: PLC0415

        return run_subprocess([PROJECT_MGT, "sync"], check=check)
