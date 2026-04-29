"""Configuration management for pyproject.toml.

Provides the PyprojectConfigFile class, which generates and validates the project's
pyproject.toml according to PEP 518, 621, and 660. Covers project metadata,
runtime and development dependencies, build system configuration, and tool settings.
"""

import platform
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

import spdx_matcher
from packaging.version import Version

from pyrig.core.resources import (
    resource_content,
)
from pyrig.core.strings import (
    package_req_name_split_pattern,
)
from pyrig.rig import resources
from pyrig.rig.cli import cli
from pyrig.rig.configs.base.config_file import ConfigDict, Priority
from pyrig.rig.configs.base.toml import TomlConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_coverage_tester import ProjectCoverageTester
from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.security_checker import SecurityChecker
from pyrig.rig.tools.type_checker import TypeChecker
from pyrig.rig.tools.version_control.remote import (
    RemoteVersionController,
)
from pyrig.rig.tools.version_control.version_controller import VersionController
from pyrig.rig.utils.versions import VersionConstraint, adjust_version_to_level


class PyprojectConfigFile(TomlConfigFile):
    """Generates and validates the project's pyproject.toml file.

    Builds the complete configuration structure from live project data: project
    metadata sourced from git and the filesystem, runtime and development
    dependencies, build system configuration for uv, and opinionated tool settings
    for ruff, ty, pytest, and bandit.

    Created at priority 20 so that other configuration files can read its values
    during their own generation.

    Subclasses can override accessor methods such as ``dependencies``,
    ``dev_dependencies``, or ``requires_python`` to customise the generated file.
    """

    def priority(self) -> float:
        """Return the creation priority (20), ensuring pyproject.toml is written early.

        A higher priority means earlier execution. Priority 20 causes this file to
        be created before most other config files, which may need to read project
        metadata from it.
        """
        return Priority.MEDIUM

    def parent_path(self) -> Path:
        """Return the project root directory."""
        return Path()

    def stem(self) -> str:
        """Return ``"pyproject"``, the filename stem."""
        return "pyproject"

    def _configs(self) -> ConfigDict:
        """Build the complete pyproject.toml configuration structure.

        Reads live project state to assemble the full configuration dict that will be
        written to pyproject.toml. The returned structure covers:

        - ``project``: PEP 621 metadata (name, version, description, authors,
          license, classifiers, scripts, URLs).
        - ``dependency-groups``: Development dependencies merged from all registered
          tools via ``Tool.subclasses_dev_dependencies``.
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
        repo_owner = VersionController.I.repo_owner(check_repo_url=False)
        tests_package_root = ProjectTester.I.tests_package_root().as_posix()

        # local import as ReadmeConfigFile inherits from BadgesMarkdownConfigFile
        # which needs pyproject info for badges, and pyproject needs the
        # readme path for metadata. This avoids circular import issues.
        from pyrig.rig.configs.markdown.readme import ReadmeConfigFile  # noqa: PLC0415

        return {
            "project": {
                "name": PackageManager.I.project_name(),
                "version": self.project_version(),
                "description": self.project_description(),
                "readme": ReadmeConfigFile.I.path().as_posix(),
                "requires-python": self.requires_python(),
                "dependencies": self.make_dependency_versions(self.dependencies()),
                "authors": [
                    {"name": repo_owner},
                ],
                "maintainers": [
                    {"name": repo_owner},
                ],
                "license": self.detect_project_license(),
                "license-files": [LicenseConfigFile.I.path().as_posix()],
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
                    PackageManager.I.project_name(): (
                        f"{cli.__name__}:{cli.main.__name__}"
                    )
                },
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
                PythonLinter.I.name(): {
                    "lint": {
                        "select": ["ALL"],
                        "ignore": ["D203", "D213", "COM812", "ANN401"],
                        "fixable": ["ALL"],
                        "per-file-ignores": {
                            f"**/{tests_package_root}/**/*.py": ["S101"],
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
                        "testpaths": [f"{tests_package_root}"],
                        "addopts": " ".join(ProjectCoverageTester.I.additional_args()),
                    }
                },
                SecurityChecker.I.name(): {
                    "assert_used": {
                        "skips": [
                            # to ignore asserts for the rig tests package
                            f"*/{tests_package_root}/*.py",
                            # to ignore asserts in test folders like tests/test_utils/
                            f"*/{ProjectTester.I.test_module_prefix()}*/*.py",
                        ],
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
        licenses: dict[str, ConfigDict]
        licenses, _ = spdx_matcher.analyse_license_text(content)
        licenses = licenses["licenses"]
        if not licenses:
            msg = "No license detected in provided content."
            raise LookupError(msg)
        return next(iter(licenses))

    def project_version(self, default: str = "0.1.0") -> str:
        """Read the project version from pyproject.toml.

        Args:
            default: Fallback value when the ``version`` key is absent. Defaults
                to ``"0.1.0"``, matching uv's initial scaffold value.

        Returns:
            Version string from pyproject.toml, or ``default`` if absent.
        """
        return str(self.load().get("project", {}).get("version", default))

    def project_description(self, default: str = "Add your description here") -> str:
        """Read the project description from pyproject.toml.

        Args:
            default: Fallback value when the ``description`` key is absent. Defaults
                to ``"Add your description here"``, matching uv's initial scaffold.

        Returns:
            Description string from pyproject.toml, or ``default`` if absent.
        """
        return str(self.load().get("project", {}).get("description", default))

    def make_python_version_classifiers(self) -> list[str]:
        """Build the PyPI trove classifiers for the project.

        Generates a ``Programming Language :: Python :: X.Y`` classifier for every
        Python minor version in the project's supported range (derived from
        ``requires-python``), plus the fixed classifiers
        ``Operating System :: OS Independent`` and ``Typing :: Typed``.

        Returns:
            List of trove classifier strings, ready for the ``project.classifiers``
            field in pyproject.toml.
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

    def make_dependency_versions(
        self,
        dependencies: Iterable[str],
        additional: Iterable[str] | None = None,
    ) -> list[str]:
        """Merge and normalise two dependency lists into one sorted, deduplicated list.

        Packages already present in ``dependencies`` (matched by package name,
        ignoring version specifiers) are excluded from ``additional`` before merging.
        This prevents a tool from overwriting a user-pinned version. The final list
        is sorted alphabetically.

        Args:
            dependencies: Primary dependency list. All entries are kept as-is.
            additional: Optional supplementary dependencies. An entry is only included
                if its package name does not already appear in ``dependencies``.

        Returns:
            Sorted, deduplicated list combining both inputs.
        """
        if additional is None:
            additional = ()
        stripped_dependencies = {
            self.remove_version_from_dep(dep) for dep in dependencies
        }
        filtered_additional = (
            dep
            for dep in additional
            if self.remove_version_from_dep(dep) not in stripped_dependencies
        )
        # Due to caching in load(), mutating in place causes bugs.
        # Always return a new structure instead of modifying.
        return sorted({*dependencies, *filtered_additional})

    def remove_version_from_dep(self, dep: str) -> str:
        """Strip the version specifier from a dependency string.

        Splits on all operator characters using the pattern from
        ``pyrig.core.strings.package_req_name_split_pattern`` and returns the
        first element.

        Args:
            dep: Dependency string with or without a version specifier
                (e.g., ``"requests>=2.0,<3"`` or ``"requests"``).

        Returns:
            Package name with any version specifier removed
            (e.g., ``"requests>=2.0,<3"`` → ``"requests"``).
        """
        return package_req_name_split_pattern().split(dep)[0]

    def dependencies(self, default: list[str] | None = None) -> list[str]:
        """Read runtime dependencies from pyproject.toml.

        Args:
            default: Fallback list when the ``project.dependencies`` key is absent.
                Defaults to a list containing the current pyrig package name.

        Returns:
            List of dependency strings from pyproject.toml, or ``default`` if absent.
        """
        if default is None:
            default = [Pyrigger.I.name()]
        deps: list[str] = self.load().get("project", {}).get("dependencies", default)
        return deps

    def dev_dependencies(self) -> list[str]:
        """Read development dependencies from pyproject.toml.

        Returns:
            List of dependency strings from ``dependency-groups.dev``, or an empty
            list if that section is absent.
        """
        dev_deps: list[str] = self.load().get("dependency-groups", {}).get("dev", [])
        return dev_deps

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
        constraint = self.load()["project"]["requires-python"]
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

    def requires_python(self, default: str | None = None) -> str:
        """Read the requires-python constraint from pyproject.toml.

        Args:
            default: Fallback specifier when the ``requires-python`` key is absent.
                When ``None`` (the default), constructs ``">=<current minor version>"``
                from the running Python interpreter (e.g., ``">=3.10"``).

        Returns:
            PEP 440 version specifier string (e.g., ``">=3.10"``).
        """
        if default is None:
            current_version = adjust_version_to_level(
                Version(platform.python_version()), level="minor"
            )
            default = f">={current_version}"
        return str(self.load().get("project", {}).get("requires-python", default))

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
