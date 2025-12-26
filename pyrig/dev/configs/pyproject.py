"""Configuration management for pyproject.toml files.

This module provides the PyprojectConfigFile class for managing the project's
pyproject.toml file, which is the central configuration file for Python projects
following PEP 518, PEP 621, and PEP 660.

The PyprojectConfigFile class handles:
    - Project metadata (name, version, description, authors, URLs)
    - Runtime and development dependencies
    - Build system configuration (uv build backend)
    - Tool configurations for ruff, ty, pytest, bandit, and rumdl
    - Python version constraints and classifiers

The configuration enforces pyrig's opinionated defaults:
    - All ruff linting rules enabled (except D203, D213, COM812, ANN401)
    - Google-style docstring convention
    - Strict ty type checking with error-on-warning
    - Bandit security scanning (excluding test directories)
    - Markdown linting with rumdl
    - uv as the build backend

Note:
    The validation uses subset checking, so users can add additional tool
    configurations (e.g., [tool.mypy]) beyond what pyrig generates. The file
    is considered valid as long as it contains all required configurations.
    - Coverage threshold enforcement via pytest

The class provides utility methods for:
    - Querying project information (name, version, description)
    - Managing dependencies (runtime, dev, and standard dev deps)
    - Fetching and validating Python versions
    - Detecting project license from LICENSE file
    - Generating Python version classifiers

Note:
    This config file has priority 20, meaning it's initialized early in the
    ConfigFile initialization process, as other config files may depend on
    reading values from pyproject.toml.
"""

import re
from functools import cache
from pathlib import Path
from typing import Any, Literal

import requests
import spdx_matcher  # type: ignore[import-untyped]
from packaging.version import Version

from pyrig.dev.cli import cli
from pyrig.dev.configs.base.toml import TomlConfigFile
from pyrig.dev.utils.resources import return_resource_content_on_fetch_error
from pyrig.dev.utils.versions import VersionConstraint, adjust_version_to_level
from pyrig.src.consts import STANDARD_DEV_DEPS
from pyrig.src.git import (
    get_github_pages_url_from_git,
    get_repo_owner_and_name_from_git,
    get_repo_url_from_git,
)
from pyrig.src.modules.package import (
    get_pkg_name_from_cwd,
    get_pkg_name_from_project_name,
    get_project_name_from_cwd,
)
from pyrig.src.testing.convention import (
    COVERAGE_THRESHOLD,
    TESTS_PACKAGE_NAME,
)


class PyprojectConfigFile(TomlConfigFile):
    """Configuration file manager for pyproject.toml.

    This class manages the project's pyproject.toml file, which serves as the central
    configuration for Python projects. It extends TomlConfigFile to provide specialized
    handling for project metadata, dependencies, build configuration, and tool settings.

    The class automatically generates a complete pyproject.toml structure with:
        - Project metadata extracted from git and filesystem
        - Dependency management with version normalization
        - Build system configuration using uv
        - Tool configurations for linting, type checking, testing, and security
        - CLI entry points derived from the project structure

    Key Features:
        - **Automatic Metadata**: Extracts project name, owner, and URLs from git
        - **License Detection**: Automatically detects license from LICENSE file
        - **Python Version Management**: Fetches latest Python versions from API
        - **Dependency Normalization**: Merges and deduplicates dependencies
        - **Opinionated Defaults**: Enforces pyrig's recommended tool configurations

    Priority:
        This config file has priority 20, ensuring it's created early in the
        initialization process since other config files may read from it.

    Examples:
        Get project information::

            from pyrig.dev.configs.pyproject import PyprojectConfigFile

            # Get project name
            name = PyprojectConfigFile.get_project_name()

            # Get all dependencies
            deps = PyprojectConfigFile.get_all_dependencies()

            # Get supported Python versions
            versions = PyprojectConfigFile.get_supported_python_versions()

        Initialize the config file::

            # Creates or updates pyproject.toml with defaults
            PyprojectConfigFile()

    See Also:
        pyrig.dev.configs.base.toml.TomlConfigFile
            Base class for TOML configuration files
        pyrig.src.consts.STANDARD_DEV_DEPS
            Standard development dependencies added by pyrig
    """

    @classmethod
    def get_priority(cls) -> float:
        """Get the priority for this config file.

        Returns:
            float: Priority value of 20. Higher values are initialized first.
                This file has elevated priority because other config files may
                need to read project metadata from pyproject.toml during their
                initialization.
        """
        return 20

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to pyproject.toml with dependency normalization.

        This method normalizes dependencies before writing to ensure consistency.
        It removes incorrect version specifiers and merges standard dev dependencies.

        Args:
            config: The configuration dictionary to write. Must contain 'project'
                and 'dependency-groups' keys with dependency lists.

        Raises:
            TypeError: If config is not a dict.

        Note:
            This method modifies the config dict in-place via
            remove_wrong_dependencies() before writing.
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to pyproject.toml file."
            raise TypeError(msg)
        # remove the versions from the dependencies
        cls.remove_wrong_dependencies(config)
        super().dump(config)

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for pyproject.toml.

        Returns:
            Path: Empty Path() representing the project root directory.
        """
        return Path()

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the expected pyproject.toml configuration structure.

        This method generates a complete pyproject.toml configuration by:
            - Extracting project metadata from git (owner, repo URL)
            - Reading current project state (name, version, description)
            - Detecting license from LICENSE file
            - Fetching Python version constraints
            - Merging runtime and development dependencies
            - Configuring build system and tool settings

        Returns:
            dict[str, Any]: Complete pyproject.toml configuration with keys:
                - project: Project metadata, dependencies, and entry points
                - dependency-groups: Development dependencies
                - build-system: uv build backend configuration
                - tool: Configurations for uv, ruff, ty, pytest, bandit, rumdl

        Note:
            This method makes external calls to:
                - Git for owner, repo name and URLs
                - LICENSE file for license detection
                - pyproject.toml for current version and description
        """
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
                "maintainers": [
                    {"name": repo_owner},
                ],
                "license": cls.detect_project_licence(),
                "license-files": ["LICENSE"],
                "requires-python": cls.get_project_requires_python(),
                "classifiers": [
                    *cls.make_python_version_classifiers(),
                ],
                "urls": {
                    "Homepage": get_repo_url_from_git(),
                    "Documentation": get_github_pages_url_from_git(),
                    "Source": get_repo_url_from_git(),
                    "Issues": f"{get_repo_url_from_git()}/issues",
                    "Changelog": f"{get_repo_url_from_git()}/releases",
                },
                "keywords": [],
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
                    "exclude": [".*"],
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
                "ty": {
                    "terminal": {
                        "error-on-warning": True,
                    },
                },
                "rumdl": {
                    "respect_gitignore": True,
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
    def detect_project_licence(cls) -> str:
        """Detect the project's license from the LICENSE file.

        Reads the LICENSE file and uses spdx_matcher to identify the license
        type and return its SPDX identifier.

        Returns:
            str: SPDX license identifier (e.g., "MIT", "Apache-2.0", "GPL-3.0").

        Raises:
            FileNotFoundError: If LICENSE file doesn't exist.
            StopIteration: If no license is detected in the file.

        Note:
            This method reads from the LICENSE file in the project root.
        """
        content = Path("LICENSE").read_text(encoding="utf-8")
        licenses: dict[str, dict[str, Any]]
        licenses, _ = spdx_matcher.analyse_license_text(content)
        licenses = licenses["licenses"]
        return next(iter(licenses))

    @classmethod
    def remove_wrong_dependencies(cls, config: dict[str, Any]) -> None:
        """Normalize dependencies by removing incorrect version specifiers.

        This method processes both runtime and development dependencies to ensure
        they follow the correct format and removes any malformed version specifiers.

        Args:
            config: The configuration dict to modify in place. Must contain
                'project.dependencies' and 'dependency-groups.dev' keys.

        Note:
            This method modifies the config dict in-place.
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
            str: The project description from project.description field,
                or empty string if not found.

        Note:
            This method reads from the pyproject.toml file on disk.
        """
        return str(cls.load().get("project", {}).get("description", ""))

    @classmethod
    def get_project_version(cls) -> str:
        """Get the project version from pyproject.toml.

        Returns:
            str: The project version from project.version field,
                or empty string if not found.

        Note:
            This method reads from the pyproject.toml file on disk.
        """
        return str(cls.load().get("project", {}).get("version", ""))

    @classmethod
    def make_python_version_classifiers(cls) -> list[str]:
        """Generate PyPI classifiers for supported Python versions.

        Creates a list of PyPI trove classifiers including:
            - Python version classifiers for each supported version
            - Operating system classifier (OS Independent)
            - Typing classifier (Typed)

        Returns:
            list[str]: List of PyPI classifiers, e.g.:
                ["Programming Language :: Python :: 3.12",
                 "Programming Language :: Python :: 3.13",
                 "Operating System :: OS Independent",
                 "Typing :: Typed"]

        Note:
            This method calls get_supported_python_versions() which may make
            an API call to fetch the latest Python version.
        """
        versions = cls.get_supported_python_versions()
        python_version_classifiers = [
            f"Programming Language :: Python :: {v.major}.{v.minor}" for v in versions
        ]
        os_classifiers = [
            "Operating System :: OS Independent",
        ]
        typing_classifiers = [
            "Typing :: Typed",
        ]

        return [*python_version_classifiers, *os_classifiers, *typing_classifiers]

    @classmethod
    def get_project_requires_python(cls, default: str = ">=3.12") -> str:
        """Get the project's Python version requirement from pyproject.toml.

        Args:
            default: Default value to return if requires-python is not found.
                Defaults to ">=3.12".

        Returns:
            str: The requires-python constraint (e.g., ">=3.12", ">=3.10,<4.0"),
                or the default value if not found.

        Note:
            This method reads from the pyproject.toml file on disk.
        """
        return str(cls.load().get("project", {}).get("requires-python", default))

    @classmethod
    def make_dependency_versions(
        cls,
        dependencies: list[str],
        additional: list[str] | None = None,
    ) -> list[str]:
        """Normalize and merge dependency lists with deduplication.

        This method:
            1. Strips version specifiers from dependencies for comparison
            2. Filters out additional dependencies that are already present
            3. Merges the lists and removes duplicates
            4. Returns a sorted list

        Args:
            dependencies: Primary dependencies to process. Can include version
                specifiers (e.g., ["requests>=2.0", "click"]).
            additional: Additional dependencies to merge. Only added if not
                already present in dependencies (based on package name).
                Defaults to None.

        Returns:
            list[str]: Sorted, deduplicated list of dependencies with version
                specifiers preserved from the original lists.

        Examples:
            >>> make_dependency_versions(
            ...     ["requests>=2.0", "click"],
            ...     ["requests>=3.0", "typer"]
            ... )
            ['click', 'requests>=2.0', 'typer']
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

        Removes version constraints and extras from a dependency string,
        leaving only the package name.

        Args:
            dep: Dependency string with optional version specifier
                (e.g., "requests>=2.0", "click[dev]", "typer==0.9.0").

        Returns:
            str: Package name without version or extras (e.g., "requests",
                "click", "typer").

        Examples:
            >>> remove_version_from_dep("requests>=2.0")
            'requests'
            >>> remove_version_from_dep("click[dev]")
            'click'
        """
        return re.split(r"[^a-zA-Z0-9_.-]", dep)[0]

    @classmethod
    def get_package_name(cls) -> str:
        """Get the Python package name (with underscores).

        Converts the project name (which may use hyphens) to a valid Python
        package name (using underscores).

        Returns:
            str: The package name derived from the project name
                (e.g., "my_project" from "my-project").

        Note:
            This method reads from the pyproject.toml file on disk.
        """
        project_name = cls.get_project_name()
        return get_pkg_name_from_project_name(project_name)

    @classmethod
    def get_project_name(cls) -> str:
        """Get the project name from pyproject.toml.

        Returns:
            str: The project name from project.name field,
                or empty string if not found.

        Note:
            This method reads from the pyproject.toml file on disk.
        """
        return str(cls.load().get("project", {}).get("name", ""))

    @classmethod
    def get_all_dependencies(cls) -> list[str]:
        """Get all dependencies (runtime and development).

        Combines runtime dependencies from project.dependencies and development
        dependencies from dependency-groups.dev.

        Returns:
            list[str]: Combined list of all dependencies with version specifiers.

        Note:
            This method reads from the pyproject.toml file on disk.
        """
        all_deps = cls.get_dependencies()
        all_deps.extend(cls.get_dev_dependencies())
        return all_deps

    @classmethod
    def get_standard_dev_dependencies(cls) -> list[str]:
        """Get pyrig's standard development dependencies.

        Returns the standard set of development dependencies that pyrig adds
        to all projects (e.g., ruff, ty, pytest, etc.).

        Returns:
            list[str]: Sorted list of standard dev dependencies from
                STANDARD_DEV_DEPS constant.

        See Also:
            pyrig.src.consts.STANDARD_DEV_DEPS
                The constant defining standard dependencies
        """
        # sort the dependencies
        return sorted(STANDARD_DEV_DEPS)

    @classmethod
    def get_dev_dependencies(cls) -> list[str]:
        """Get development dependencies from pyproject.toml.

        Returns:
            list[str]: List of dev dependencies from dependency-groups.dev,
                or empty list if not found.

        Note:
            This method reads from the pyproject.toml file on disk.
        """
        dev_deps: list[str] = cls.load().get("dependency-groups", {}).get("dev", [])
        return dev_deps

    @classmethod
    def get_dependencies(cls) -> list[str]:
        """Get runtime dependencies from pyproject.toml.

        Returns:
            list[str]: List of runtime dependencies from project.dependencies,
                or empty list if not found.

        Note:
            This method reads from the pyproject.toml file on disk.
        """
        deps: list[str] = cls.load().get("project", {}).get("dependencies", [])
        return deps

    @classmethod
    @return_resource_content_on_fetch_error(resource_name="LATEST_PYTHON_VERSION")
    @cache
    def fetch_latest_python_version(cls) -> str:
        """Fetch the latest stable Python version from endoflife.date API.

        Makes an HTTP request to the endoflife.date API to get the latest
        stable Python version. The result is cached for the lifetime of the
        process. On error, returns a fallback version from resources.

        Returns:
            str: The latest stable Python version (e.g., "3.13.1").

        Raises:
            requests.HTTPError: If the API request fails and no fallback is
                available.

        Note:
            This method is cached and makes an external API call. The
            @return_resource_content_on_fetch_error decorator provides a
            fallback value if the API is unavailable.
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
        """Get the latest stable Python version at the specified precision level.

        Fetches the latest Python version and adjusts it to the requested
        precision level (e.g., 3.13.1 -> 3.13 for "minor" level).

        Args:
            level: Version precision level. Options:
                - "major": Returns X.0 (e.g., 3.0)
                - "minor": Returns X.Y (e.g., 3.13)
                - "micro": Returns X.Y.Z (e.g., 3.13.1)
                Defaults to "minor".

        Returns:
            Version: The latest stable Python version adjusted to the specified
                precision level.

        Raises:
            requests.HTTPError: If the API request fails and no fallback is
                available.

        Note:
            This method makes an external API call via fetch_latest_python_version().
        """
        latest_version = Version(cls.fetch_latest_python_version())
        return adjust_version_to_level(latest_version, level)

    @classmethod
    def get_latest_possible_python_version(
        cls, level: Literal["major", "minor", "micro"] = "micro"
    ) -> Version:
        """Get the latest Python version allowed by the requires-python constraint.

        Parses the requires-python constraint from pyproject.toml and returns
        the upper bound. If no upper bound is specified, returns the latest
        stable Python version.

        Args:
            level: Version precision level. Options:
                - "major": Returns X.0 (e.g., 3.0)
                - "minor": Returns X.Y (e.g., 3.13)
                - "micro": Returns X.Y.Z (e.g., 3.13.1)
                Defaults to "micro".

        Returns:
            Version: The latest allowed Python version at the specified
                precision level.

        Note:
            This method reads from the pyproject.toml file on disk and may
            make an external API call if no upper bound is specified.

        Examples:
            For requires-python = ">=3.10,<3.14"::

                >>> get_latest_possible_python_version("minor")
                Version('3.13')

            For requires-python = ">=3.10" (no upper bound)::

                >>> get_latest_possible_python_version("minor")
                Version('3.13')  # Latest stable version
        """
        constraint = cls.load()["project"]["requires-python"]
        version_constraint = VersionConstraint(constraint)
        version = version_constraint.get_upper_inclusive()
        if version is None:
            version = cls.get_latest_python_version()

        return adjust_version_to_level(version, level)

    @classmethod
    def get_first_supported_python_version(cls) -> Version:
        """Get the minimum supported Python version from requires-python.

        Parses the requires-python constraint and returns the lower bound.

        Returns:
            Version: The minimum Python version (e.g., Version('3.12') for
                requires-python = ">=3.12").

        Raises:
            ValueError: If no lower bound is specified in requires-python.

        Note:
            This method reads from the pyproject.toml file on disk.

        Examples:
            For requires-python = ">=3.10"::

                >>> get_first_supported_python_version()
                Version('3.10')
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
        """Get all supported Python minor versions within the constraint range.

        Parses the requires-python constraint and returns all minor versions
        within the range (e.g., for ">=3.10,<3.14" returns [3.10, 3.11, 3.12, 3.13]).

        Returns:
            list[Version]: List of supported Python minor versions, sorted in
                ascending order.

        Note:
            This method reads from the pyproject.toml file on disk and may
            make an external API call to determine the upper bound if not
            specified in requires-python.

        Examples:
            For requires-python = ">=3.10,<3.13"::

                >>> get_supported_python_versions()
                [Version('3.10'), Version('3.11'), Version('3.12')]

            For requires-python = ">=3.12" (no upper bound)::

                >>> get_supported_python_versions()
                [Version('3.12'), Version('3.13')]  # Up to latest stable
        """
        constraint = cls.get_project_requires_python()
        version_constraint = VersionConstraint(constraint)
        return version_constraint.get_version_range(
            level="minor", upper_default=cls.get_latest_python_version()
        )
