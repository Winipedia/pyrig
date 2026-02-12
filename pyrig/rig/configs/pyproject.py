"""Manages pyproject.toml (PEP 518, 621, 660).

Handles metadata, dependencies, build config (uv), tool configs (ruff, ty, pytest,
bandit, rumdl). Enforces opinionated defaults: all ruff rules (except D203, D213,
COM812, ANN401), Google docstrings, strict ty, bandit security, coverage threshold.
Validation uses subset checking (users can add extra configs). Priority 20 (created
early for other configs to read).

Utility methods: project info, dependencies, Python versions, license detection,
classifiers.
"""

from functools import cache
from pathlib import Path
from typing import Any, Literal

import requests
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
from pyrig.rig.utils.resources import return_resource_content_on_fetch_error
from pyrig.rig.utils.versions import VersionConstraint, adjust_version_to_level
from pyrig.src.modules.package import (
    pkg_name_from_cwd,
    pkg_name_from_project_name,
    project_name_from_cwd,
)
from pyrig.src.string_ import pkg_req_name_split_pattern


class PyprojectConfigFile(TomlConfigFile):
    """Manages pyproject.toml with metadata, dependencies, build config, tool settings.

    Generates structure with metadata from git/filesystem, dependency normalization,
    uv build config, tool configs, CLI entry points. Priority 20 (created early).

    Features: auto metadata, license detection, Python version management, dependency
    normalization, opinionated defaults.

    See Also:
        pyrig.rig.configs.base.toml.TomlConfigFile
        pyrig.src.consts.STANDARD_DEV_DEPS
    """

    @classmethod
    def priority(cls) -> float:
        """Return priority 20 (created early for other configs to read)."""
        return Priority.MEDIUM

    @classmethod
    def _dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write config with dependency normalization (modifies in-place)."""
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to pyproject.toml file."
            raise TypeError(msg)
        cls.remove_wrong_dependencies(config)
        super()._dump(config)

    @classmethod
    def parent_path(cls) -> Path:
        """Return project root."""
        return Path()

    @classmethod
    def _configs(cls) -> dict[str, Any]:
        """Generate complete pyproject.toml config (metadata, deps, build, tools)."""
        repo_owner, _ = VersionController.L.repo_owner_and_name(check_repo_url=False)
        tests_pkg_name = MirrorTestConfigFile.L.tests_package_name()

        return {
            "project": {
                "name": project_name_from_cwd(),
                "version": cls.project_version(),
                "description": cls.project_description(),
                "readme": "README.md",
                "authors": [
                    {"name": repo_owner},
                ],
                "maintainers": [
                    {"name": repo_owner},
                ],
                "license": cls.detect_project_license(),
                "license-files": [LicenseConfigFile.L.path().name],
                "requires-python": cls.requires_python(),
                "classifiers": [
                    *cls.make_python_version_classifiers(),
                ],
                "urls": {
                    "Homepage": RemoteVersionController.L.repo_url(),
                    "Documentation": DocsBuilder.L.documentation_url(),
                    "Source": RemoteVersionController.L.repo_url(),
                    "Issues": RemoteVersionController.L.get_issues_url(),
                    "Changelog": RemoteVersionController.L.releases_url(),
                },
                "keywords": [],
                "scripts": {
                    project_name_from_cwd(): f"{cli.__name__}:{cli.main.__name__}"
                },
                "dependencies": cls.make_dependency_versions(cls.dependencies()),
            },
            "dependency-groups": {
                "dev": cls.make_dependency_versions(
                    cls.dev_dependencies(),
                    additional=Tool.subclasses_dev_dependencies(),
                )
            },
            "build-system": {
                "requires": PackageManager.L.build_system_requires(),
                "build-backend": PackageManager.L.build_backend(),
            },
            "tool": {
                "uv": {
                    "build-backend": {
                        "module-name": pkg_name_from_cwd(),
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
                            f"**/{tests_pkg_name}/**/*.py": ["S101"],
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
                        "testpaths": [tests_pkg_name],
                        "addopts": f"--cov={pkg_name_from_cwd()} --cov-report=term-missing --cov-fail-under={ProjectTester.L.coverage_threshold()}",  # noqa: E501
                    }
                },
                "bandit": {
                    "exclude_dirs": [
                        ".*",
                    ],
                    "assert_used": {
                        "skips": [
                            f"*/{tests_pkg_name}/*.py",
                        ],
                    },
                },
            },
        }

    @classmethod
    def detect_project_license(cls) -> str:
        """Detect the project's license from the LICENSE file.

        Reads the LICENSE file and uses spdx_matcher to identify the license
        type and return its SPDX identifier.

        Returns:
            str: SPDX license identifier (e.g., "MIT", "Apache-2.0", "GPL-3.0").

        Raises:
            FileNotFoundError: If LICENSE file doesn't exist.
            StopIteration: If no license is detected (empty licenses dict).

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

    @classmethod
    def remove_wrong_dependencies(cls, config: dict[str, Any]) -> None:
        """Normalize dependency versions (modifies in-place)."""
        config["project"]["dependencies"] = cls.make_dependency_versions(
            config["project"]["dependencies"]
        )
        config["dependency-groups"]["dev"] = cls.make_dependency_versions(
            config["dependency-groups"]["dev"]
        )

    @classmethod
    def project_description(cls) -> str:
        """Get project description from pyproject.toml."""
        return str(cls.load().get("project", {}).get("description", ""))

    @classmethod
    def project_version(cls) -> str:
        """Get project version from pyproject.toml."""
        return str(cls.load().get("project", {}).get("version", ""))

    @classmethod
    def make_python_version_classifiers(cls) -> list[str]:
        """Generate PyPI classifiers (Python versions, OS Independent, Typed)."""
        versions = cls.supported_python_versions()
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
    def requires_python(cls, default: str = ">=3.12") -> str:
        """Get requires-python constraint from pyproject.toml."""
        return str(cls.load().get("project", {}).get("requires-python", default))

    @classmethod
    def make_dependency_versions(
        cls,
        dependencies: list[str],
        additional: list[str] | None = None,
    ) -> list[str]:
        """Normalize and merge dependency lists (sorted, deduplicated)."""
        if additional is None:
            additional = []
        stripped_dependencies = {
            cls.remove_version_from_dep(dep) for dep in dependencies
        }
        additional = [
            dep
            for dep in additional
            if cls.remove_version_from_dep(dep) not in stripped_dependencies
        ]
        # Due to caching in load(), mutating in place causes bugs.
        # Always return a new structure instead of modifying.
        dependencies = [*dependencies, *additional]
        return sorted(set(dependencies))

    @classmethod
    def remove_version_from_dep(cls, dep: str) -> str:
        """Strip version specifier from dependency.

        Uses REQ_NAME_SPLIT_PATTERN from package module for consistency.
        (e.g., 'requests>=2.0' -> 'requests').
        """
        return pkg_req_name_split_pattern().split(dep)[0]

    @classmethod
    def package_name(cls) -> str:
        """Get Python package name with underscores.

        (e.g., 'my-project' -> 'my_project').
        """
        project_name = cls.project_name()
        return pkg_name_from_project_name(project_name)

    @classmethod
    def project_name(cls) -> str:
        """Get project name from pyproject.toml."""
        return str(cls.load().get("project", {}).get("name", ""))

    @classmethod
    def dev_dependencies(cls) -> list[str]:
        """Get dev dependencies from pyproject.toml."""
        dev_deps: list[str] = cls.load().get("dependency-groups", {}).get("dev", [])
        return dev_deps

    @classmethod
    def dependencies(cls) -> list[str]:
        """Get runtime dependencies from pyproject.toml."""
        deps: list[str] = cls.load().get("project", {}).get("dependencies", [])
        return deps

    @classmethod
    @cache
    @return_resource_content_on_fetch_error(resource_name="LATEST_PYTHON_VERSION")
    def fetch_latest_python_version(
        cls, level: Literal["major", "minor", "micro"] = "minor"
    ) -> str:
        """Fetch latest stable Python version.

        Is fetched from endoflife.date API (cached, with fallback).
        """
        url = "https://endoflife.date/api/python.json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data: list[dict[str, str]] = resp.json()
        latest_version = data[0]["latest"]
        return str(adjust_version_to_level(Version(latest_version), level))

    @classmethod
    def latest_python_version(
        cls, level: Literal["major", "minor", "micro"] = "minor"
    ) -> Version:
        """Get latest stable Python version at precision level (major/minor/micro)."""
        latest_version = Version(cls.fetch_latest_python_version())
        return adjust_version_to_level(latest_version, level)

    @classmethod
    def latest_possible_python_version(
        cls, level: Literal["major", "minor", "micro"] = "micro"
    ) -> Version:
        """Get latest Python version allowed by requires-python constraint."""
        constraint = cls.load()["project"]["requires-python"]
        version_constraint = VersionConstraint(constraint)
        version = version_constraint.upper_inclusive()
        if version is None:
            version = cls.latest_python_version()

        return adjust_version_to_level(version, level)

    @classmethod
    def first_supported_python_version(cls) -> Version:
        """Get minimum supported Python version from requires-python."""
        constraint = cls.requires_python()
        version_constraint = VersionConstraint(constraint)
        lower = version_constraint.find_lower_inclusive()
        if lower is None:
            msg = "Need a lower bound for python version"
            raise ValueError(msg)
        return lower

    @classmethod
    def supported_python_versions(cls) -> list[Version]:
        """Get all supported Python minor versions within requires-python constraint."""
        constraint = cls.requires_python()
        version_constraint = VersionConstraint(constraint)
        return version_constraint.version_range(
            level="minor", upper_default=cls.latest_python_version()
        )
