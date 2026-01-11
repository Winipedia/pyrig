"""Markdown badge file configuration management.

Provides BadgesMarkdownConfigFile for creating Markdown files with auto-generated
project badges from pyproject.toml and Git metadata.

Example:
    >>> from pathlib import Path
    >>> from pyrig.dev.configs.base.badges_md import BadgesMarkdownConfigFile
    >>>
    >>> class ReadmeFile(BadgesMarkdownConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path()
    ...
    ...     @classmethod
    ...     def get_filename(cls) -> str:
    ...         return "README"
    >>>
    >>> ReadmeFile()  # Creates README.md with badges
"""

import pyrig
from pyrig.dev.configs.base.markdown import MarkdownConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow
from pyrig.dev.configs.workflows.release import ReleaseWorkflow
from pyrig.dev.management.remote_version_controller import RemoteVersionController
from pyrig.dev.management.version_controller import VersionController
from pyrig.dev.utils.urls import (
    get_codecov_url,
    get_pypi_badge_url,
    get_pypi_url,
)


class BadgesMarkdownConfigFile(MarkdownConfigFile):
    """Base class for Markdown files with auto-generated project badges.

    Generates badges from pyproject.toml and Git metadata. Validates that file
    contains required badges, project name, and description.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the Markdown file

    See Also:
        pyrig.dev.configs.base.markdown.MarkdownConfigFile: Parent class
        pyrig.dev.configs.pyproject.PyprojectConfigFile: Project metadata
        pyrig.src.git: Git repository utilities
    """

    @classmethod
    def get_lines(cls) -> list[str]:
        """Generate Markdown with project name, categorized badges, and description.

        Returns:
            Formatted Markdown with H1 header, badge categories, and description.
        """
        project_name = PyprojectConfigFile.L.get_project_name()
        badges = cls.get_badges()
        badges_lines: list[str] = []
        for badge_category, badge_list in badges.items():
            badges_lines.append(f"<!-- {badge_category} -->")
            badges_lines.extend(badge_list)
        description = PyprojectConfigFile.L.get_project_description()
        return [
            f"# {project_name}",
            "",
            *badges_lines,
            "",
            "---",
            "",
            f"> {description}",
            "",
            "---",
            "",
        ]

    @classmethod
    def get_badges(cls) -> dict[str, list[str]]:
        """Get categorized badges from project metadata and Git info.

        Returns:
            Dict mapping category names (tooling, code-quality, package-info, ci/cd,
            documentation) to lists of badge Markdown strings.
        """
        python_versions = PyprojectConfigFile.L.get_supported_python_versions()
        joined_python_versions = "|".join(str(v) for v in python_versions)
        health_check_wf_name = HealthCheckWorkflow.get_filename()
        release_wf_name = ReleaseWorkflow.get_filename()
        return {
            "tooling": [
                rf"[![{pyrig.__name__}](https://img.shields.io/badge/built%20with-{pyrig.__name__}-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/{pyrig.__name__})",
                r"[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)",
                r"[![Container](https://img.shields.io/badge/Container-Podman-A23CD6?logo=podman&logoColor=grey&colorA=0D1F3F&colorB=A23CD6)](https://podman.io/)",
                r"[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)",
                r"[![MkDocs](https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white)](https://www.mkdocs.org/)",
            ],
            "code-quality": [
                r"[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)",
                r"[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)",
                r"[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)",
                r"[![pytest](https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest)](https://pytest.org/)",
                rf"[![codecov]({get_codecov_url()}/branch/{VersionController.L.get_default_branch()}/graph/badge.svg)]({get_codecov_url()})",
                r"[![rumdl](https://img.shields.io/badge/markdown-rumdl-darkgreen)](https://github.com/rvben/rumdl)",
            ],
            "package-info": [
                rf"[![PyPI]({get_pypi_badge_url()})]({get_pypi_url()})",
                rf"[![Python](https://img.shields.io/badge/python-{joined_python_versions}-blue.svg?logo=python&logoColor=white)](https://www.python.org/)",
                rf"[![License]({RemoteVersionController.L.get_license_badge_url()})]({RemoteVersionController.L.get_repo_url()}/blob/main/LICENSE)",
            ],
            "ci/cd": [
                rf"[![CI]({RemoteVersionController.L.get_cicd_badge_url(health_check_wf_name, 'CI', 'github')})]({RemoteVersionController.L.get_cicd_url(health_check_wf_name)})",  # noqa: E501
                rf"[![CD]({RemoteVersionController.L.get_cicd_badge_url(release_wf_name, 'CD', 'github')})]({RemoteVersionController.L.get_cicd_url(release_wf_name)})",  # noqa: E501
            ],
            "documentation": [
                rf"[![Documentation](https://img.shields.io/badge/Docs-GitHub%20Pages-black?style=for-the-badge&logo=github&logoColor=white)]({RemoteVersionController.L.get_documentation_url()})",
            ],
        }
