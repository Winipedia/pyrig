"""Config utilities for poetry and pyproject.toml."""

from functools import cache
from pathlib import Path
from typing import Any, cast

import requests
from packaging.version import Version

from pyrig.dev.configs.base.base import TomlConfigFile
from pyrig.dev.configs.python.experiment import ExperimentConfigFile
from pyrig.src.os.os import run_subprocess
from pyrig.src.project.poetry.dev_deps import DEV_DEPENDENCIES
from pyrig.src.project.poetry.versions import VersionConstraint
from pyrig.src.testing.convention import TEST_MODULE_PREFIX, TESTS_PACKAGE_NAME


class PyprojectConfigFile(TomlConfigFile):
    """Config file for pyproject.toml."""

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file.

        We remove the wrong dependencies from the config before dumping.
        So we do not want dependencies under tool.poetry.dependencies but
        under project.dependencies. And we do not want dev dependencies under
        tool.poetry.dev-dependencies but under tool.poetry.group.dev.dependencies.
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to pyproject.toml file."
            raise TypeError(msg)
        config = cls.remove_wrong_dependencies(config)
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
                "dynamic": ["dependencies"],
                "scripts": {
                    cls.get_project_name(): f"{cli.__name__}:{cli.main.__name__}"
                },
            },
            "build-system": {
                "requires": ["poetry-core>=2.0.0,<3.0.0"],
                "build-backend": "poetry.core.masonry.api",
            },
            "tool": {
                "poetry": {
                    "packages": [
                        {
                            "include": cls.get_pkg_name_from_cwd(),
                        }
                    ],
                    "dependencies": cls.make_dependency_to_version_dict(
                        cls.get_dependencies()
                    ),
                    "group": {
                        "dev": {
                            "dependencies": cls.make_dependency_to_version_dict(
                                cls.get_dev_dependencies(),
                                additional=DEV_DEPENDENCIES,
                            )
                        }
                    },
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
                    "exclude_dirs": ["./" + ExperimentConfigFile.get_path().as_posix()],
                    "assert_used": {
                        "skips": [f"*{TEST_MODULE_PREFIX}*.py"],
                    },
                },
            },
        }

    @classmethod
    def make_dependency_to_version_dict(
        cls,
        dependencies: dict[str, str | dict[str, str]],
        additional: dict[str, str | dict[str, str]] | None = None,
    ) -> dict[str, str | dict[str, str]]:
        """Make a dependency to version dict.

        Args:
            dependencies: Dependencies to add
            additional: Additional dependencies to add

        Returns:
            Dependency to version dict
        """
        if additional is None:
            additional = {}
        dependencies.update(additional)
        dep_to_version_dict: dict[str, str | dict[str, str]] = {}
        for dep, version in dependencies.items():
            at_file_dep = " @ file://"
            if at_file_dep in dep:
                dep_new, path = dep.split(at_file_dep)
                dep_to_version_dict[dep_new] = {"path": path}
                continue
            if isinstance(version, dict):
                dep_to_version_dict[dep] = version
                continue
            dep_to_version_dict[dep] = "*"
        return dep_to_version_dict

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
    def remove_wrong_dependencies(cls, config: dict[str, Any]) -> dict[str, Any]:
        """Remove the wrong dependencies from the config."""
        # raise if the right sections do not exist
        if config.get("tool", {}).get("poetry", {}).get("dependencies") is None:
            msg = "No dependencies section in config"
            raise ValueError(msg)

        if (
            config.get("tool", {}).get("poetry", {}).get("group", {}).get("dev", {})
            is None
        ):
            msg = "No dev dependencies section in config"
            raise ValueError(msg)

        # remove the wrong dependencies sections if they exist
        if config.get("project", {}).get("dependencies") is not None:
            del config["project"]["dependencies"]
        if config.get("tool", {}).get("poetry", {}).get("dev-dependencies") is not None:
            del config["tool"]["poetry"]["dev-dependencies"]

        return config

    @classmethod
    def get_all_dependencies(cls) -> dict[str, str | dict[str, str]]:
        """Get all dependencies."""
        all_deps = cls.get_dependencies()
        all_deps.update(cls.get_dev_dependencies())
        return all_deps

    @classmethod
    def get_dev_dependencies(cls) -> dict[str, str | dict[str, str]]:
        """Get the dev dependencies."""
        dev_deps: dict[str, str | dict[str, str]] = (
            cls.load().get("tool", {}).get("poetry", {}).get("dev-dependencies", {})
        )
        tool_dev_deps = (
            cls.load()
            .get("tool", {})
            .get("poetry", {})
            .get("group", {})
            .get("dev", {})
            .get("dependencies", {})
        )
        dev_deps.update(tool_dev_deps)
        return dev_deps

    @classmethod
    def get_dependencies(cls) -> dict[str, str | dict[str, str]]:
        """Get the dependencies."""
        deps_raw = set(cls.load().get("project", {}).get("dependencies", {}))
        deps = {
            d.split("(")[0].strip(): d.split("(")[1].split(")")[0].strip()
            if "(" in d
            else "*"
            for d in deps_raw
        }

        tool_deps = cls.load().get("tool", {}).get("poetry", {}).get("dependencies", {})
        deps.update(tool_deps)
        return deps

    @classmethod
    def get_authors(cls) -> list[dict[str, str]]:
        """Get the authors."""
        return cast(
            "list[dict[str, str]]", cls.load().get("project", {}).get("authors", [])
        )

    @classmethod
    def get_main_author(cls) -> dict[str, str]:
        """Get the main author.

        Assumes the main author is the first author.
        """
        return cls.get_authors()[0]

    @classmethod
    def get_main_author_name(cls) -> str:
        """Get the main author name."""
        return cls.get_main_author()["name"]

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
    def update_dependencies(cls, *, check: bool = True) -> None:
        """Update the dependencies."""
        run_subprocess(["poetry", "update", "--with", "dev"], check=check)

    @classmethod
    def install_dependencies(cls, *, check: bool = True) -> None:
        """Install the dependencies."""
        run_subprocess(["poetry", "install", "--with", "dev"], check=check)
