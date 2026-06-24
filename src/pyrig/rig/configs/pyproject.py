"""Configuration management for pyproject.toml.

Provides the PyprojectConfigFile class, which generates and validates the project's
pyproject.toml according to PEP 518, 621, and 660. Covers project metadata,
runtime and development dependencies, build system configuration, and tool settings.
"""

import platform
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal

import spdx_matcher
from packaging.version import Version

import pyrig
from pyrig.core.introspection.modules import leaf_module_name
from pyrig.core.resources import (
    resource_content,
)
from pyrig.core.strings import (
    dependency_requirement_as_package_name,
    snake_to_kebab_case,
)
from pyrig.core.version import VersionConstraint, adjust_version_to_level
from pyrig.rig import resources, tests
from pyrig.rig.cli import main
from pyrig.rig.configs.base.config_file import Priority
from pyrig.rig.configs.base.toml import TOMLConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.dependencies.checker import DependencyChecker
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.security_checker import SecurityChecker
from pyrig.rig.tools.testers.coverage import CoverageTester
from pyrig.rig.tools.testers.project import ProjectTester
from pyrig.rig.tools.type_checker import TypeChecker
from pyrig.rig.tools.version_control.remote import (
    RemoteVersionController,
)
from pyrig.rig.tools.version_control.version_controller import VersionController


class PyprojectConfigFile(TOMLConfigFile):
    """Generates and validates the project's pyproject.toml file.

    Builds the complete configuration structure from live project data: project
    metadata sourced from git and the filesystem, runtime and development
    dependencies, build system configuration for uv, and opinionated tool settings
    for ruff, ty, pytest, and bandit.

    Validated at priority -10, the lowest among all config files, so it runs after
    ``LicenseConfigFile`` and all other default-priority files have been processed.

    Subclasses can override accessor methods such as ``dependencies``,
    ``dev_dependencies``, or ``requires_python`` to customise the generated file.
    """

    def priority(self) -> float:
        """Return a priority step below the LICENSE file's, ensuring late validation.

        A higher priority means earlier validation. Positioning this file one step
        below ``LicenseConfigFile`` guarantees the LICENSE exists first (its text
        is read to auto-detect the SPDX identifier). Because no other config file
        overrides priority, ``pyproject.toml`` validates last among all config files.
        """
        return Priority.decrease(LicenseConfigFile.I.priority())

    def parent_path(self) -> Path:
        """Return the project root directory."""
        return Path()

    def stem(self) -> str:
        """Return ``"pyproject"``, the filename stem."""
        return "pyproject"

    def _configs(self) -> dict[str, Any]:
        """Build the complete pyproject.toml configuration structure.

        Reads live project state to assemble the full configuration dict that will be
        written to pyproject.toml. The returned structure covers:

        - ``project``: PEP 621 metadata (name, version, description, authors,
          license, scripts, URLs).
        - ``dependency-groups``: Development dependencies from pyproject.toml merged
          with additional entries contributed by all registered tools via
          ``Tool.subclasses_dev_dependencies``.
        - ``build-system``: uv build backend configuration.
        - ``tool``: Opinionated settings for ruff (all rules, Google docstrings),
          ty (error-on-warning), pytest (with coverage), and bandit (security checks).

        Note:
            ``ReadmeConfigFile`` is imported locally to break a circular dependency:
            the readme config needs pyproject data for badge generation, while
            pyproject needs the readme path for project metadata.

        Returns:
            Nested dict matching the expected pyproject.toml structure.
        """
        # local import as ReadmeConfigFile inherits from BadgesConfigFile
        # which needs pyproject info for badges, and pyproject needs the
        # readme path for metadata. This avoids circular import issues.
        from pyrig.rig.configs.readme import ReadmeConfigFile  # noqa: PLC0415

        repo_owner = VersionController.I.repo_owner()
        rig_tests_dir_name = leaf_module_name(tests)
        return {
            "project": {
                "name": PackageManager.I.project_name(),
                "version": self.project_version(),
                "description": self.project_description(),
                "readme": ReadmeConfigFile.I.path().as_posix(),
                "requires-python": self.requires_python(),
                "dependencies": self.dependencies(),
                "authors": [
                    {"name": repo_owner},
                ],
                "maintainers": [
                    {"name": repo_owner},
                ],
                "license": self.detect_project_license(),
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
                    )
                },
            },
            "dependency-groups": {
                "dev": self.merge_additional_dependencies(
                    dependencies=self.dev_dependencies(),
                    additional=Tool.subclasses_dev_dependencies(),
                )
            },
            "build-system": {
                "requires": PackageManager.I.build_system_requires(),
                "build-backend": PackageManager.I.build_backend(),
            },
            "tool": {
                PythonLinter.I.name(): {
                    "lint": {
                        "select": ["ALL"],
                        "ignore": ["COM812", "ANN401"],
                        "fixable": ["ALL"],
                        "per-file-ignores": {
                            f"**/{rig_tests_dir_name}/**/*.py": ["S101"],
                        },
                        "pydocstyle": {"convention": PythonLinter.I.pydocstyle()},
                    },
                },
                TypeChecker.I.name(): {
                    "terminal": {
                        "error-on-warning": True,
                    },
                },
                ProjectTester.I.name(): {
                    "ini_options": {
                        "testpaths": [ProjectTester.I.tests_package_root().as_posix()],
                        "addopts": str(CoverageTester.I.additional_test_args()),
                    }
                },
                SecurityChecker.I.name(): {
                    "assert_used": {
                        "skips": [
                            # to ignore asserts for the rig tests package
                            f"*/{rig_tests_dir_name}/*.py",
                            # to ignore asserts in test folders like tests/test_utils/
                            f"*/{ProjectTester.I.test_module_prefix()}*/*.py",
                        ],
                    },
                },
                DependencyChecker.I.name(): {
                    "root": PackageManager.I.source_root().as_posix(),
                    "per_rule_ignores": {
                        "DEP002": [snake_to_kebab_case(pyrig.__name__)]
                    },
                },
            },
        }

    def detect_project_license(self) -> str:
        """Detect the SPDX license identifier from the project LICENSE file.

        Reads the LICENSE file via ``LicenseConfigFile`` and delegates detection to
        ``detect_project_licence_from_content``.

        Returns:
            SPDX license identifier (e.g., ``"MIT"``, ``"Apache-2.0"``).

        Raises:
            FileNotFoundError: If the LICENSE file does not exist.
            LookupError: If no license can be identified in the LICENSE file.
        """
        content = LicenseConfigFile.I.read_content()
        return self.detect_project_licence_from_content(content)

    def detect_project_licence_from_content(self, content: str) -> str:
        """Detect the SPDX license identifier from a string of text.

        Passes ``content`` to ``spdx_matcher.analyse_license_text`` and returns
        the identifier of the first matched license.

        Args:
            content: Text to analyse, typically the contents of a LICENSE file.

        Returns:
            SPDX license identifier (e.g., ``"MIT"``, ``"Apache-2.0"``).

        Raises:
            LookupError: If ``spdx_matcher`` finds no recognisable license in the
                text.
        """
        licenses: dict[str, dict[str, Any]]
        licenses, _ = spdx_matcher.analyse_license_text(content)
        licenses = licenses["licenses"]
        if not licenses:
            msg = "No license detected in provided content."
            raise LookupError(msg)
        return next(iter(licenses))

    def project_version(self) -> str:
        """Read the project version from pyproject.toml.

        Returns:
            Version string from pyproject.toml, or ``"0.1.0"`` if absent
            (matching uv's initial scaffold value).
        """
        return self.load().get("project", {}).get("version", "0.1.0")

    def project_description(self) -> str:
        """Read the project description from pyproject.toml.

        Returns:
            Description string from pyproject.toml, or
            ``"Add your description here"`` if absent (matching uv's initial scaffold).
        """
        return (
            self.load()
            .get("project", {})
            .get("description", "Add your description here")
        )

    def merge_additional_dependencies(
        self,
        dependencies: Iterable[str],
        additional: Iterable[str],
    ) -> list[str]:
        """Merge and normalise two dependency lists into one sorted, deduplicated list.

        Packages already present in ``dependencies`` (matched by package name,
        ignoring version specifiers) are excluded from ``additional`` before merging.
        This prevents a tool from overwriting a user-pinned version. The final list
        is sorted alphabetically.

        Args:
            dependencies: Primary dependency list. All entries are kept as-is.
            additional: Supplementary dependencies. An entry is only included
                if its package name does not already appear in ``dependencies``.

        Returns:
            Sorted, deduplicated list combining both inputs.
        """
        dependencies = set(dependencies)
        normalized_dependencies = {
            dependency_requirement_as_package_name(dep) for dep in dependencies
        }
        additional = (
            dep
            for dep in additional
            if dependency_requirement_as_package_name(dep)
            not in normalized_dependencies
        )
        # Due to caching in load(), mutating in place causes bugs.
        # Always return a new structure instead of modifying.
        return sorted({*dependencies, *additional})

    def dependencies(self) -> list[str]:
        """Read runtime dependencies from pyproject.toml.

        Returns:
            List of dependency strings from pyproject.toml, or an empty list if absent.
        """
        return self.load().get("project", {}).get("dependencies", [])

    def dev_dependencies(self) -> list[str]:
        """Read development dependencies from pyproject.toml.

        Returns:
            List of dependency strings from ``dependency-groups.dev``, or an empty
            list if that section is absent.
        """
        return self.load().get("dependency-groups", {}).get("dev", [])

    def latest_possible_python_version(
        self, level: Literal["major", "minor", "micro"] = "minor"
    ) -> Version:
        """Get the highest Python version permitted by the requires-python constraint.

        Reads the ``requires-python`` specifier from pyproject.toml and derives the
        upper inclusive bound. When the specifier has no upper bound
        (e.g., ``">=3.10"``), falls back to the latest known stable Python release.

        Args:
            level: Precision of the returned version. Defaults to ``"minor"``
                (e.g., ``Version("3.11")`` rather than ``Version("3.11.5")``). See
                ``adjust_version_to_level`` for details on each level.

        Returns:
            The highest allowed Python version at the requested precision level.
        """
        constraint = self.requires_python()
        version_constraint = VersionConstraint(constraint)
        version = version_constraint.upper_inclusive()
        if version is None:
            version = self.latest_python_version(level=level)

        return adjust_version_to_level(version, level)

    def first_supported_python_version(self) -> Version:
        """Return the minimum Python version required by the project.

        Reads the lower bound of the ``requires-python`` specifier from
        pyproject.toml.

        Returns:
            Lowest inclusive Python version supported by the project.

        Raises:
            LookupError: If the ``requires-python`` constraint has no lower bound.
        """
        constraint = self.requires_python()
        version_constraint = VersionConstraint(constraint)
        lower = version_constraint.find_lower_inclusive()
        if lower is None:
            msg = "Need a lower bound for python version"
            raise LookupError(msg)
        return lower

    def supported_python_versions(self) -> tuple[Version, ...]:
        """Return all Python minor versions within the requires-python range.

        Reads the ``requires-python`` specifier from pyproject.toml and expands it
        into a tuple of minor-precision Version objects. The upper end of an unbounded
        range is capped at the latest known stable Python release.

        Returns:
            Tuple of Version objects, one per supported minor version, in ascending
            order.
        """
        constraint = self.requires_python()
        version_constraint = VersionConstraint(constraint)
        return version_constraint.version_range(
            level="minor",
            upper_default=self.latest_python_version(level="minor"),
        )

    def requires_python(self) -> str:
        """Read the requires-python constraint from pyproject.toml.

        If the field is absent, defaults to a specifier that matches the current Python
        version (e.g., ``">=3.12"`` for Python 3.12), ensuring that the generated
        pyproject.toml is always valid.

        Returns:
            PEP 440 version specifier string (e.g., ``">=3.13"``).
        """
        current_version = adjust_version_to_level(
            Version(platform.python_version()), level="minor"
        )
        return (
            self.load()
            .get("project", {})
            .get("requires-python", f">={current_version}")
        )

    def latest_python_version(
        self, level: Literal["major", "minor", "micro"] = "minor"
    ) -> Version:
        """Return the latest known stable Python version.

        Reads the version from the bundled ``LATEST_PYTHON_VERSION`` resource file
        and truncates it to the requested precision level.

        Args:
            level: Precision of the returned version. Defaults to ``"minor"``
                (e.g., ``Version("3.13")``). See ``adjust_version_to_level`` for
                details on each level.

        Returns:
            Latest stable Python version at the requested precision level.
        """
        latest_version = Version(resource_content("LATEST_PYTHON_VERSION", resources))
        return adjust_version_to_level(latest_version, level)
