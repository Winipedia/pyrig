"""Generation and validation of the project's `pyproject.toml` file."""

import platform
from pathlib import Path
from typing import Any, Literal

from packaging.version import Version
from pyrig_runtime.core.dependencies.distribution import (
    distribution_requirement_as_module_name,
)
from pyrig_runtime.rig.cli import main

from pyrig.core.iterate import deep_sorted_dict
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
from pyrig.rig.tools.packages.manager import PackageManager
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
    registered tools. Individual pieces of the structure can be customized by
    overriding the corresponding accessor method in a subclass.
    """

    def validate(self) -> bool:
        """Validate the config file, then add any dependencies still missing.

        Returns:
            `True` if the file was already correct and no dependency was
            added; `False` otherwise.
        """
        correct = super().validate()
        dependencies = self.add_additional_dependencies()
        return correct and not dependencies

    def merge_configs(self) -> dict[str, Any]:
        """Merge the required configuration structure.

        Returns:
            The merged configuration structure.
        """
        configs = super().merge_configs()
        self.merge_build_system_requires(configs)
        return configs

    def merge_build_system_requires(self, configs: dict[str, Any]) -> None:
        """Set `build-system.requires` in `configs` to the canonical value.

        Overwrites any existing value; this key is never left as-is or
        merged with what the file already had.

        Args:
            configs: The configuration structure to update. Modified in-place.
        """
        configs["build-system"]["requires"] = PackageManager.I.build_system_requires()

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
                "license": LicenseConfigFile.I.spdx_identifier(),
                "license-files": [LicenseConfigFile.I.path().as_posix()],
                "authors": self.authors_configs(),
                "maintainers": self.maintainers_configs(),
                "dependencies": [],
                "urls": deep_sorted_dict(self.url_configs()),
                "scripts": {
                    PackageManager.I.project_name(): (
                        f"{main.__name__}:{main.main.__name__}"
                    ),
                },
            },
            "dependency-groups": {
                "dev": [],
            },
            "build-system": {
                "requires": PackageManager.I.build_system_requires(),
                "build-backend": PackageManager.I.build_backend(),
            },
            "tool": deep_sorted_dict(self.tool_configs()),
        }

    def maintainers_configs(self) -> list[dict[str, Any]]:
        """Assemble the required `maintainers` section of `pyproject.toml`.

        Identical to `authors`.
        """
        return self.authors_configs()

    def authors_configs(self) -> list[dict[str, Any]]:
        """Assemble the required `authors` section of `pyproject.toml`."""
        return [
            {
                "name": VersionController.I.repo_owner(),
                "email": self.maintainer_email(),
            },
        ]

    def url_configs(self) -> dict[str, Any]:
        """Assemble the required `urls` section of `pyproject.toml`."""
        return {
            "Changelog": RemoteVersionController.I.releases_url(),
            "Documentation": DocsBuilder.I.documentation_url(),
            "Homepage": RemoteVersionController.I.repo_url(),
            "Issues": RemoteVersionController.I.issues_url(),
            "Source": RemoteVersionController.I.repo_url(),
        }

    def tool_configs(self) -> dict[str, Any]:
        """Assemble the required `tool` section of `pyproject.toml`.

        Starts from whatever `tool` configuration already exists on disk,
        then layers each managed tool's required configuration on top.

        Returns:
            The existing `tool` section merged with the managed tools'
            required configuration.
        """
        return {
            **self.tool_section(),
            DependencyChecker.I.config_name(): {
                "root": PackageManager.I.source_root().as_posix(),
                "per_rule_ignores": {"DEP002": [Pyrigger.I.runtime_dependency()]},
            },
            ProjectTester.I.config_name(): {
                "testpaths": [ProjectTester.I.package_root().as_posix()],
                "addopts": sorted(ProjectTester.I.additional_args()),
                "filterwarnings": ["error"],
                "strict": True,
            },
            PythonLinter.I.config_name(): {
                "lint": {
                    "select": ["ALL"],
                    "ignore": [f"{'C'}PY001"],
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

    def removable(self) -> bool:
        """Return `False` to prevent removal of the `pyproject.toml` file."""
        return False

    def stem(self) -> str:
        """Return `"pyproject"`."""
        return "pyproject"

    def add_additional_dependencies(self) -> tuple[str, ...]:
        """Add whichever required runtime and dev dependencies are missing.

        Compares the project's dependencies against
        `Pyrigger.I.runtime_dependencies()`, and its dev dependencies against
        `Tool.subclasses_dev_dependencies()`. Anything missing is added via
        the package manager, the environment is synced so the new packages
        are actually installed, then the file is reloaded and re-dumped so
        its formatting matches pyrig's conventions again.

        Returns:
            The dependencies that were added, empty if none were missing.
        """
        current_dependencies = set(
            map(distribution_requirement_as_module_name, self.dependencies()),
        )
        dependencies = tuple(
            dependency
            for dependency in Pyrigger.I.runtime_dependencies()
            if distribution_requirement_as_module_name(dependency)
            not in current_dependencies
        )

        current_dev_dependencies = set(
            map(distribution_requirement_as_module_name, self.dev_dependencies()),
        )
        dev_dependencies = tuple(
            dependency
            for dependency in Tool.subclasses_dev_dependencies()
            if distribution_requirement_as_module_name(dependency)
            not in current_dev_dependencies
        )
        if dependencies:
            PackageManager.I.add_args(*dependencies).run()
        if dev_dependencies:
            PackageManager.I.add_group_dev_args(*dev_dependencies).run()
        if dependencies or dev_dependencies:
            PackageManager.I.install_dependencies().run()
            self.load.cache_clear()
            self.dump(self.load())

        return (*dependencies, *dev_dependencies)

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

    def tool_section(self) -> dict[str, Any]:
        """Read the `tool` section from `pyproject.toml`.

        Returns:
            Dict of tool configurations from `pyproject.toml`, or an empty dict
            if that section is absent.
        """
        return self.load().get("tool", {})

    def first_supported_python_version(self) -> Version:
        """Return the minimum Python version required by the project.

        Returns:
            Lowest inclusive Python version supported by the project.

        Raises:
            LookupError: If the requires-python constraint has no lower bound.
        """
        lower = VersionConstraint(self.requires_python()).find_lower_inclusive()
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
        return adjust_version_to_level(
            VersionConstraint(self.requires_python()).find_upper_inclusive(
                default=self.latest_python_version(level=level),
            ),
            level,
        )

    def supported_python_versions(self) -> tuple[Version, ...]:
        """Return all Python minor versions within the requires-python range.

        The upper end of an unbounded range is capped at the latest known
        stable Python release.

        Returns:
            Tuple of Version objects, one per supported minor version, in
            ascending order.
        """
        return VersionConstraint(self.requires_python()).version_range(
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

        If the field is absent, defaults to a lower-bound specifier requiring
        at least the currently running Python version (e.g., `">=3.12"` for
        Python 3.12).

        Returns:
            PEP 440 version specifier string (e.g., `">=3.13"`).
        """
        return (
            self.load()
            .get("project", {})
            .get(
                "requires-python",
                f">={
                    adjust_version_to_level(
                        Version(platform.python_version()),
                        level='minor',
                    )
                }",
            )
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

    def maintainer_email(self) -> str:
        """Read the author's email from `pyproject.toml`.

        Returns:
            Email string from `pyproject.toml`, or the configured git user
            email if absent.
        """
        return (
            self.load().get("project", {}).get("authors", [{}])[0].get("email")
        ) or VersionController.I.email()
