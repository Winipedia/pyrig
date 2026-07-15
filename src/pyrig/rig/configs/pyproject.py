"""Generation and validation of the project's `pyproject.toml` file."""

import platform
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal

from packaging.version import Version
from pyrig_runtime.core.strings import (
    dependency_requirement_as_module_name,
)
from pyrig_runtime.rig.cli import main

from pyrig.core.iterate import deep_sort_dict
from pyrig.core.resources import (
    resource_content,
)
from pyrig.core.version import VersionConstraint, adjust_version_to_level
from pyrig.rig import resources
from pyrig.rig.configs.base.config_file import Priority
from pyrig.rig.configs.base.toml import TOMLConfigFile
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.dependencies.checker import DependencyChecker
from pyrig.rig.tools.docs.builder import DocsBuilder
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.testing.project import ProjectTester
from pyrig.rig.tools.version_control.controller import VersionController
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class PyprojectConfigFile(TOMLConfigFile):
    """The project's `pyproject.toml` file, derived from live project state.

    The required configuration structure is assembled from project metadata,
    dependencies, build system settings, and tool configuration rather than
    hard-coded, so it always reflects the current state of the project and its
    registered tools. Individual pieces of the structure can be customised by
    overriding the corresponding accessor method in a subclass.
    """

    def _configs(self) -> dict[str, Any]:
        """Assemble the required `pyproject.toml` structure from live project state.

        Returns:
            Nested dict matching the expected `pyproject.toml` structure.
        """
        # pyproject.toml sometimes has info other config files need and vice versa.
        # to avoid local imports of PyprojectConfigFile spread across the project
        # we centralize local imports of the other config files here.
        from pyrig.rig.configs.community.license import (  # noqa: PLC0415
            LicenseConfigFile,
        )
        from pyrig.rig.configs.readme import (  # noqa: PLC0415
            ReadmeConfigFile,
        )

        return {
            "project": {
                "name": PackageManager.I.project_name(),
                "version": self.project_version(),
                "description": self.project_description(),
                "readme": ReadmeConfigFile.I.path().as_posix(),
                "requires-python": self.requires_python(),
                "dependencies": self.merge_additional_dependencies(
                    dependencies=self.dependencies(),
                    additional=self.additional_dependencies(),
                ),
                "authors": [
                    {"name": VersionController.I.repo_owner()},
                ],
                "maintainers": [
                    {"name": VersionController.I.repo_owner()},
                ],
                "license": LicenseConfigFile.I.spdx_identifier(),
                "license-files": [LicenseConfigFile.I.path().as_posix()],
                "urls": {
                    "Homepage": RemoteVersionController.I.repo_url(),
                    "Documentation": DocsBuilder.I.documentation_url(),
                    "Source": RemoteVersionController.I.repo_url(),
                    "Issues": RemoteVersionController.I.issues_url(),
                    "Changelog": RemoteVersionController.I.releases_url(),
                },
                "scripts": {
                    PackageManager.I.project_name(): (
                        f"{main.__name__}:{main.main.__name__}"
                    ),
                },
            },
            "dependency-groups": {
                "dev": self.merge_additional_dependencies(
                    dependencies=self.dev_dependencies(),
                    additional=self.additional_dev_dependencies(),
                ),
            },
            "build-system": {
                "requires": PackageManager.I.build_system_requires(),
                "build-backend": PackageManager.I.build_backend(),
            },
            "tool": deep_sort_dict(self.tool_configs()),
        }

    def tool_configs(self) -> dict[str, Any]:
        """Assemble the required `tool` section of `pyproject.toml`."""
        return {
            DependencyChecker.I.config_name(): {
                "root": PackageManager.I.source_root().as_posix(),
                "per_rule_ignores": {"DEP002": [Pyrigger.I.runtime_dependency()]},
            },
            ProjectTester.I.config_name(): {
                "testpaths": [ProjectTester.I.package_root().as_posix()],
                "addopts": list(ProjectTester.I.additional_args()),
                "filterwarnings": ["error"],
                "strict": True,
            },
            PythonLinter.I.config_name(): {
                "lint": {
                    "select": ["ALL"],
                    "per-file-ignores": {
                        f"{ProjectTester.I.package_name()}/**/*.py": ["S101"],
                    },
                    "pydocstyle": {"convention": PythonLinter.I.pydocstyle()},
                },
                "format": {
                    "docstring-code-format": True,
                },
            },
        }

    def parent_path(self) -> Path:
        """Return the project root directory."""
        return Path()

    def priority(self) -> float:
        """Return a priority one step above the default.

        Ensures validation before all default-priority config files.
        """
        return Priority.increase(super().priority())

    def stem(self) -> str:
        """Return `"pyproject"`."""
        return "pyproject"

    def additional_dependencies(self) -> list[str]:
        """Return the runtime dependencies required in addition to `dependencies()`."""
        return [Pyrigger.I.runtime_dependency()]

    def additional_dev_dependencies(self) -> list[str]:
        """Return the dev dependencies required in addition to `dev_dependencies()`."""
        return Tool.subclasses_dev_dependencies()

    def dependencies(self) -> list[str]:
        """Read runtime dependencies from `pyproject.toml`.

        Returns:
            List of dependency strings from `pyproject.toml`, or an empty list
            if absent.
        """
        return self.load().get("project", {}).get("dependencies", [])

    def dev_dependencies(self) -> list[str]:
        """Read development dependencies from `pyproject.toml`.

        Returns:
            List of dependency strings from `dependency-groups.dev`, or an empty
            list if that section is absent.
        """
        return self.load().get("dependency-groups", {}).get("dev", [])

    def merge_additional_dependencies(
        self,
        dependencies: Iterable[str],
        additional: Iterable[str],
    ) -> list[str]:
        """Merge and normalise two dependency lists into one sorted, deduplicated list.

        Packages already present in `dependencies` (matched by package name,
        ignoring version specifiers) are excluded from `additional` before merging.
        This prevents a tool from overwriting a user-pinned version.

        Args:
            dependencies: Primary dependency list. All entries are kept as-is.
            additional: Supplementary dependencies. An entry is only included
                if its package name does not already appear in `dependencies`.

        Returns:
            Sorted, deduplicated list combining both inputs.
        """
        dependencies = set(dependencies)
        normalized_dependencies = {
            dependency_requirement_as_module_name(dep) for dep in dependencies
        }
        additional = (
            dep
            for dep in additional
            if dependency_requirement_as_module_name(dep) not in normalized_dependencies
        )
        return sorted({*dependencies, *additional})

    def first_supported_python_version(self) -> Version:
        """Return the minimum Python version required by the project.

        Returns:
            Lowest inclusive Python version supported by the project.

        Raises:
            LookupError: If the requires-python constraint has no lower bound.
        """
        constraint = self.requires_python()
        version_constraint = VersionConstraint(constraint)
        lower = version_constraint.find_lower_inclusive()
        if lower is None:
            msg = "lower bound for python version is required"
            raise LookupError(msg)
        return lower

    def latest_possible_python_version(
        self,
        level: Literal["major", "minor", "micro"] = "minor",
    ) -> Version:
        """Return the highest Python version allowed by the requires-python constraint.

        When the constraint has no upper bound (e.g., `">=3.10"`), falls back to
        the latest known stable Python release.

        Args:
            level: Precision of the returned version. Defaults to `"minor"`
                (e.g., `Version("3.11")` rather than `Version("3.11.5")`).

        Returns:
            The highest allowed Python version at the requested precision level.
        """
        constraint = self.requires_python()
        version_constraint = VersionConstraint(constraint)
        version = version_constraint.find_upper_inclusive(
            default=self.latest_python_version(level=level),
        )
        return adjust_version_to_level(version, level)

    def supported_python_versions(self) -> tuple[Version, ...]:
        """Return all Python minor versions within the requires-python range.

        The upper end of an unbounded range is capped at the latest known
        stable Python release.

        Returns:
            Tuple of Version objects, one per supported minor version, in
            ascending order.

        Raises:
            RuntimeError: If the requires-python constraint has no lower bound.
        """
        constraint = self.requires_python()
        version_constraint = VersionConstraint(constraint)
        return version_constraint.version_range(
            level="minor",
            upper_default=self.latest_python_version(level="minor"),
        )

    def latest_python_version(
        self,
        level: Literal["major", "minor", "micro"] = "minor",
    ) -> Version:
        """Return the latest known stable Python version.

        Args:
            level: Precision of the returned version. Defaults to `"minor"`
                (e.g., `Version("3.14")`).

        Returns:
            Latest stable Python version at the requested precision level.
        """
        return adjust_version_to_level(Version(self.latest_python_version_str()), level)

    def latest_python_version_str(self) -> str:
        """Return the latest known stable Python version as a string.

        Returns:
            Latest stable Python version as a string (e.g., `"3.14.4"`).
        """
        return resource_content("LATEST_PYTHON_VERSION", resources).strip()

    def requires_python(self) -> str:
        """Read the requires-python constraint from `pyproject.toml`.

        If the field is absent, defaults to a specifier that matches the
        currently running Python version (e.g., `">=3.12"` for Python 3.12).

        Returns:
            PEP 440 version specifier string (e.g., `">=3.13"`).
        """
        current_version = adjust_version_to_level(
            Version(platform.python_version()),
            level="minor",
        )
        return (
            self.load()
            .get("project", {})
            .get("requires-python", f">={current_version}")
        )

    def project_description(self) -> str:
        """Read the project description from `pyproject.toml`.

        Returns:
            Description string from `pyproject.toml`. Defaults to uv's initial
            scaffold value, `"Add your description here"`, if absent.
        """
        return (
            self.load()
            .get("project", {})
            .get("description", "Add your description here")
        )

    def project_version(self) -> str:
        """Read the project version from `pyproject.toml`.

        Returns:
            Version string from `pyproject.toml`, or `"0.1.0"` if absent
            (matching uv's initial scaffold value).
        """
        return self.load().get("project", {}).get("version", "0.1.0")
