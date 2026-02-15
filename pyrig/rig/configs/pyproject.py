"""Manage pyproject.toml (PEP 518, 621, 660).

Handles metadata, dependencies, build config (uv), tool configs (ruff, ty, pytest,
bandit, rumdl). Enforces opinionated defaults: all ruff rules (except D203, D213,
COM812, ANN401), Google docstrings, strict ty, bandit security, coverage threshold.
Validation uses subset checking (users can add extra configs). Priority 20 (created
early for other configs to read).

Utility methods: project info, dependencies, Python versions, license detection,
classifiers.
"""

import json
from pathlib import Path
from typing import Any, Literal

import spdx_matcher
from packaging.version import Version

from pyrig.rig.cli import cli
from pyrig.rig.configs.base.base import Priority
from pyrig.rig.configs.base.toml import TomlConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.base.base import Tool
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.rig.tools.remote_version_controller import RemoteVersionController
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.resources import (
    requests_get_text_cached,
    return_resource_content_on_fetch_error,
)
from pyrig.rig.utils.versions import VersionConstraint, adjust_version_to_level
from pyrig.src.modules.package import (
    package_name_from_cwd,
    package_name_from_project_name,
    project_name_from_cwd,
)
from pyrig.src.string_ import package_req_name_split_pattern


class PyprojectConfigFile(TomlConfigFile):
    """Manage pyproject.toml with metadata, dependencies, configs, and tool settings.

    Generates structure with metadata from git/filesystem, dependency normalization,
    uv build config, tool configs, CLI entry points. Priority 20 (created early).

    Features: auto metadata, license detection, Python version management, dependency
    normalization, opinionated defaults.

    See Also:
        pyrig.rig.configs.base.toml.TomlConfigFile
    """

    def priority(self) -> float:
        """Return priority 20 (created early for other configs to read)."""
        return Priority.MEDIUM

    def _dump(self, config: dict[str, Any] | list[Any]) -> None:

        Returns:
            Priority value for config file creation order.
        """Write config with dependency normalization (modifies in-place).

        Raises:
            TypeError: If ``config`` is not a dict.
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to pyproject.toml file."
            raise TypeError(msg)
        self.remove_wrong_dependencies(config)
        super()._dump(config)

    def parent_path(self) -> Path:
        """Return project root."""
        return Path()

    def _configs(self) -> dict[str, Any]:

        Returns:
            Parent directory path.
        """Generate complete pyproject.toml config (metadata, deps, build, tools)."""
        repo_owner, _ = VersionController.I.repo_owner_and_name(check_repo_url=False)
        tests_package_name = MirrorTestConfigFile.I.tests_package_name()

        return {
            "project": {
                "name": project_name_from_cwd(),
                "version": self.project_version(),
                "description": self.project_description(),
                "readme": "README.md",
                "authors": [
                    {"name": repo_owner},
                ],
                "maintainers": [
                    {"name": repo_owner},
                ],
                "license": self.detect_project_license(),
                "license-files": [LicenseConfigFile.I.path().name],
                "requires-python": self.requires_python(),
                "classifiers": [
                    *self.make_python_version_classifiers(),
                ],
                "urls": {
                    "Homepage": RemoteVersionController.I.repo_url(),
                    "Documentation": DocsBuilder.I.documentation_url(),
                    "Source": RemoteVersionController.I.repo_url(),
                    "Issues": RemoteVersionController.I.issues_url(),
                    "Changelog": RemoteVersionController.I.releases_url(),
                },
                "keywords": [],
                "scripts": {
                    project_name_from_cwd(): f"{cli.__name__}:{cli.main.__name__}"
                },
                "dependencies": self.make_dependency_versions(self.dependencies()),
            },
            "dependency-groups": {
                "dev": self.make_dependency_versions(
                    self.dev_dependencies(),
                    additional=Tool.subclasses_dev_dependencies(),
                )
            },
            "build-system": {
                "requires": PackageManager.I.build_system_requires(),
                "build-backend": PackageManager.I.build_backend(),
            },
            "tool": {
                "uv": {
                    "build-backend": {
                        "module-name": package_name_from_cwd(),
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
                            f"**/{tests_package_name}/**/*.py": ["S101"],
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
                        "testpaths": [tests_package_name],
                        "addopts": f"--cov={package_name_from_cwd()} --cov-report=term-missing --cov-fail-under={ProjectTester.I.coverage_threshold()}",  # noqa: E501
                    }
                },
                "bandit": {
                    "exclude_dirs": [
                        ".*",
                    ],
                    "assert_used": {
                        "skips": [
                            f"*/{tests_package_name}/*.py",
                        ],
                    },
                },
            },
        }

    def detect_project_license(self) -> str:
        """Detect the project's license from the LICENSE file.

        Reads the LICENSE file and uses spdx_matcher to identify the license
        type and return its SPDX identifier.

        Returns:
            SPDX license identifier (e.g., "MIT", "Apache-2.0", "GPL-3.0").

        Raises:
            FileNotFoundError: If LICENSE file doesn't exist.
            ValueError: If no license is detected in the LICENSE file.

        Note:
            This method reads from the LICENSE file in the project root.
            May raise additional exceptions from spdx_matcher if license
            analysis fails.
        """
        content = Path("LICENSE").read_text(encoding="utf-8")
        licenses: dict[str, dict[str, Any]]
        licenses, _ = spdx_matcher.analyse_license_text(content)
        licenses = licenses["licenses"]
        if not licenses:
            msg = "No license detected in LICENSE file."
            raise ValueError(msg)
        return next(iter(licenses))

    def remove_wrong_dependencies(self, config: dict[str, Any]) -> None:
        """Normalize dependency versions (modifies in-place).

        Args:
            config: Configuration dictionary to modify.
        """
        config["project"]["dependencies"] = self.make_dependency_versions(
            config["project"]["dependencies"]
        )
        config["dependency-groups"]["dev"] = self.make_dependency_versions(
            config["dependency-groups"]["dev"]
        )

    def project_description(self) -> str:
        """Get project description from pyproject.toml.

        Returns:
            Project description string.
        """
        return str(self.load().get("project", {}).get("description", ""))

    def project_version(self) -> str:
        """Get project version from pyproject.toml.

        Returns:
            Project version string.
        """
        return str(self.load().get("project", {}).get("version", ""))

    def make_python_version_classifiers(self) -> list[str]:
        """Generate PyPI classifiers (Python versions, OS Independent, Typed).

        Returns:
            List of PyPI classifier strings.
        """
        versions = self.supported_python_versions()
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

    def requires_python(self, default: str = ">=3.12") -> str:
        """Get requires-python constraint from pyproject.toml.

        Args:
            default: Default version constraint if not found in config.

        Returns:
            Python version constraint string (e.g., ">=3.12").
        """
        return str(self.load().get("project", {}).get("requires-python", default))

    def make_dependency_versions(
        self,
        dependencies: list[str],
        additional: list[str] | None = None,
    ) -> list[str]:
        """Normalize and merge dependency lists (sorted, deduplicated).

        Args:
            dependencies: Base list of dependencies.
            additional: Optional additional dependencies to merge.

        Returns:
            Sorted, deduplicated list of dependencies.
        """
        if additional is None:
            additional = []
        stripped_dependencies = {
            self.remove_version_from_dep(dep) for dep in dependencies
        }
        additional = [
            dep
            for dep in additional
            if self.remove_version_from_dep(dep) not in stripped_dependencies
        ]
        # Due to caching in load(), mutating in place causes bugs.
        # Always return a new structure instead of modifying.
        dependencies = [*dependencies, *additional]
        return sorted(set(dependencies))

    def remove_version_from_dep(self, dep: str) -> str:
        """Strip version specifier from dependency.

        Uses ``package_req_name_split_pattern`` from ``pyrig.src.string_``
        for consistency (e.g., 'requests>=2.0' -> 'requests').

        Args:
            dep: Dependency string, optionally with version specifier.

        Returns:
            Package name without version specifier.
        """
        return package_req_name_split_pattern().split(dep)[0]

    def package_name(self) -> str:
        """Get the Python package name (e.g., 'my-project' -> 'my_project').

        Returns:
            Package name with underscores.
        """
        project_name = self.project_name()
        return package_name_from_project_name(project_name)

    def project_name(self) -> str:
        """Get project name from pyproject.toml.

        Returns:
            Project name string (e.g., "my-project").
        """
        return str(self.load().get("project", {}).get("name", ""))

    def dev_dependencies(self) -> list[str]:
        """Get dev dependencies from pyproject.toml.

        Returns:
            List of development dependency strings.
        """
        dev_deps: list[str] = self.load().get("dependency-groups", {}).get("dev", [])
        return dev_deps

    def dependencies(self) -> list[str]:
        """Get runtime dependencies from pyproject.toml.

        Returns:
            List of runtime dependency strings.
        """
        deps: list[str] = self.load().get("project", {}).get("dependencies", [])
        return deps

    @return_resource_content_on_fetch_error(resource_name="LATEST_PYTHON_VERSION")
    def fetch_latest_python_version(
        self, level: Literal["major", "minor", "micro"] = "minor"
    ) -> str:
        """Fetch latest stable Python version.

        Fetches from endoflife.date API (cached, with fallback).

        Args:
            level: Precision level for the version string.

        Returns:
            Latest Python version string at specified precision level.
        """
        url = "https://endoflife.date/api/python.json"
        data: list[dict[str, str]] = json.loads(requests_get_text_cached(url))
        latest_version = data[0]["latest"]
        return str(adjust_version_to_level(Version(latest_version), level))

    def latest_python_version(
        self, level: Literal["major", "minor", "micro"] = "minor"
    ) -> Version:
        """Get latest stable Python version at precision level (major/minor/micro).

        Args:
            level: Precision level for the version.

        Returns:
            Latest Python version object at specified precision.
        """
        latest_version = Version(self.fetch_latest_python_version())
        return adjust_version_to_level(latest_version, level)

    def latest_possible_python_version(
        self, level: Literal["major", "minor", "micro"] = "micro"
    ) -> Version:
        """Get latest Python version allowed by requires-python constraint.

        Args:
            level: Precision level for the version.

        Returns:
            Latest Python version allowed by the project's requires-python constraint.
        """
        constraint = self.load()["project"]["requires-python"]
        version_constraint = VersionConstraint(constraint)
        version = version_constraint.upper_inclusive()
        if version is None:
            version = self.latest_python_version()

        return adjust_version_to_level(version, level)

    def first_supported_python_version(self) -> Version:
        """Get minimum supported Python version from requires-python.

        Returns:
            Minimum supported Python version.

        Raises:
            ValueError: If requires-python has no lower bound.
        """
        constraint = self.requires_python()
        version_constraint = VersionConstraint(constraint)
        lower = version_constraint.find_lower_inclusive()
        if lower is None:
            msg = "Need a lower bound for python version"
            raise ValueError(msg)
        return lower

    def supported_python_versions(self) -> list[Version]:
        """Get all supported Python minor versions within requires-python constraint.

        Returns:
            List of Python versions supported by the project.
        """
        constraint = self.requires_python()
        version_constraint = VersionConstraint(constraint)
        return version_constraint.version_range(
            level="minor", upper_default=self.latest_python_version()
        )
