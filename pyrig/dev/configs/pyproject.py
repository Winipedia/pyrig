"""Config utilities for pyproject.toml."""

import re
from functools import cache
from pathlib import Path
from subprocess import CompletedProcess  # nosec: B404
from typing import Any

import requests
from packaging.version import Version

from pyrig.dev.configs.base.base import TomlConfigFile
from pyrig.dev.configs.python.experiment import ExperimentConfigFile
from pyrig.src.modules.package import DependencyGraph
from pyrig.src.os.os import run_subprocess
from pyrig.src.project.versions import VersionConstraint
from pyrig.src.testing.convention import TEST_MODULE_PREFIX, TESTS_PACKAGE_NAME


class PyprojectConfigFile(TomlConfigFile):
    """Config file for pyproject.toml."""

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to pyproject.toml file."
            raise TypeError(msg)
        # remove the versions from the dependencies
        cls.remove_wrong_dependencies(config)
        super().dump(config)

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path()

    @classmethod
    def get_project_name_from_cwd(cls) -> str:
        """Get the repository name.

        Is the parent folder the project ives in and should be the same as the
        project name.
        """
        cwd = Path.cwd()
        return cwd.name

    @classmethod
    def get_pkg_name_from_cwd(cls) -> str:
        """Get the package name from the cwd."""
        return cls.get_pkg_name_from_project_name(cls.get_project_name_from_cwd())

    @classmethod
    def get_project_description(cls) -> str:
        """Get the project description."""
        return str(cls.load().get("project", {}).get("description", ""))

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the config."""
        from pyrig.dev.cli import (  # noqa: PLC0415
            cli,
        )

        return {
            "project": {
                "name": cls.get_project_name_from_cwd(),
                "readme": "README.md",
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
                        "module-name": cls.get_pkg_name_from_cwd(),
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
                            f"{TESTS_PACKAGE_NAME}/**/*.py": ["S101"],
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
                "pytest": {"ini_options": {"testpaths": [TESTS_PACKAGE_NAME]}},
                "bandit": {
                    "exclude_dirs": [
                        "./" + ExperimentConfigFile.get_path().as_posix(),
                        ".*",
                    ],
                    "assert_used": {
                        "skips": [f"*{TEST_MODULE_PREFIX}*.py"],
                    },
                },
            },
        }

    @classmethod
    def should_remove_version_from_dep(cls) -> bool:
        """Check if we should remove the version from the dependency.

        We should remove the version if we are in a dev dependency and the dep
        is in the standard dev dependencies.
        Can be overridden by subclasses.
        """
        return True

    @classmethod
    def remove_wrong_dependencies(cls, config: dict[str, Any]) -> None:
        """Remove the wrong dependencies from the config."""
        # removes the versions from the dependencies
        config["project"]["dependencies"] = cls.make_dependency_versions(
            config["project"]["dependencies"]
        )
        config["dependency-groups"]["dev"] = cls.make_dependency_versions(
            config["dependency-groups"]["dev"]
        )

    @classmethod
    def make_dependency_versions(
        cls,
        dependencies: list[str],
        additional: list[str] | None = None,
    ) -> list[str]:
        """Make a dependency to version dict.

        Args:
            dependencies: Dependencies to add
            additional: Additional dependencies to add

        Returns:
            Dependency to version dict
        """
        if additional is None:
            additional = []
        dependencies.extend(additional)
        deps: list[str] = []
        for dep in dependencies:
            at_file_dep = "file://"
            if at_file_dep in dep:
                new_dep = dep
            elif cls.should_remove_version_from_dep():
                # remove version if it exists by split re on first non alnum or _ -
                new_dep = cls.remove_version_from_dep(dep)
            else:
                new_dep = dep
            deps.append(new_dep)
        return sorted(set(deps))

    @classmethod
    def remove_version_from_dep(cls, dep: str) -> str:
        """Remove the version from a dependency."""
        return re.split(r"[^a-zA-Z0-9_-]", dep)[0]

    @classmethod
    def get_package_name(cls) -> str:
        """Get the package name."""
        project_name = cls.get_project_name()
        return cls.get_pkg_name_from_project_name(project_name)

    @classmethod
    def get_pkg_name_from_project_name(cls, project_name: str) -> str:
        """Get the package name from the project name."""
        return project_name.replace("-", "_")

    @classmethod
    def get_project_name_from_pkg_name(cls, pkg_name: str) -> str:
        """Get the project name from the package name."""
        return pkg_name.replace("_", "-")

    @classmethod
    def get_project_name(cls) -> str:
        """Get the project name."""
        return str(cls.load().get("project", {}).get("name", ""))

    @classmethod
    def get_all_dependencies(cls) -> list[str]:
        """Get all dependencies."""
        all_deps = cls.get_dependencies()
        all_deps.extend(cls.get_dev_dependencies())
        return all_deps

    @classmethod
    def get_standard_dev_dependencies(cls) -> list[str]:
        """Get the standard dev dependencies."""
        standard_dev_dependencies: list[str] = [
            "bandit",
            "mypy",
            "pre-commit",
            "pytest",
            "pytest-mock",
            "ruff",
            "types-defusedxml",
            "types-networkx",
            "types-pyinstaller",
            "types-pyyaml",
            "types-setuptools",
            "types-tqdm",
            "pyinstaller",
        ]
        # add keyrings.alt if keyring is in dependencies
        if "keyring" in DependencyGraph.get_all_dependencies():
            standard_dev_dependencies.append("keyrings.alt")
        # sort the dependencies
        return sorted(standard_dev_dependencies)

    @classmethod
    def get_dev_dependencies(cls) -> list[str]:
        """Get the dev dependencies."""
        dev_deps: list[str] = cls.load().get("dependency-groups", {}).get("dev", [])
        return dev_deps

    @classmethod
    def get_dependencies(cls) -> list[str]:
        """Get the dependencies."""
        deps: list[str] = cls.load().get("project", {}).get("dependencies", [])
        return deps

    @classmethod
    @cache
    def fetch_latest_python_version(cls) -> Version:
        """Fetch the latest python version from python.org."""
        url = "https://endoflife.date/api/python.json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # first element has metadata for latest stable
        latest_version = data[0]["latest"]
        return Version(latest_version)

    @classmethod
    def get_latest_possible_python_version(cls) -> Version:
        """Get the latest possible python version."""
        constraint = cls.load()["project"]["requires-python"]
        version_constraint = VersionConstraint(constraint)
        version = version_constraint.get_upper_inclusive()
        if version is None:
            version = cls.fetch_latest_python_version()
        return version

    @classmethod
    def get_first_supported_python_version(cls) -> Version:
        """Get the first supported python version."""
        constraint = cls.load()["project"]["requires-python"]
        version_constraint = VersionConstraint(constraint)
        lower = version_constraint.get_lower_inclusive()
        if lower is None:
            msg = "Need a lower bound for python version"
            raise ValueError(msg)
        return lower

    @classmethod
    def get_supported_python_versions(cls) -> list[Version]:
        """Get all supported python versions."""
        constraint = cls.load()["project"]["requires-python"]
        version_constraint = VersionConstraint(constraint)
        return version_constraint.get_version_range(
            level="minor", upper_default=cls.fetch_latest_python_version()
        )

    @classmethod
    def update_dependencies(cls, *, check: bool = True) -> CompletedProcess[bytes]:
        """Update the dependencies."""
        from pyrig.src.project.mgt import PROJECT_MGT  # noqa: PLC0415

        return run_subprocess([PROJECT_MGT, "lock", "--upgrade"], check=check)

    @classmethod
    def install_dependencies(cls, *, check: bool = True) -> CompletedProcess[bytes]:
        """Install the dependencies."""
        from pyrig.src.project.mgt import PROJECT_MGT  # noqa: PLC0415

        return run_subprocess([PROJECT_MGT, "sync"], check=check)
