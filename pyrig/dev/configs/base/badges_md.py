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
from pyrig.dev.utils.git import DEFAULT_BRANCH
from pyrig.src.git import (
    get_codecov_url_from_git,
    get_github_pages_url_from_git,
    get_licence_badge_url_from_git,
    get_pypi_badge_url_from_git,
    get_pypi_url_from_git,
    get_repo_url_from_git,
    get_workflow_badge_url_from_git,
    get_workflow_run_url_from_git,
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
        project_name = PyprojectConfigFile.get_project_name()
        badges = cls.get_badges()
        badges_lines: list[str] = []
        for badge_category, badge_list in badges.items():
            badges_lines.append(f"<!-- {badge_category} -->")
            badges_lines.extend(badge_list)
        description = PyprojectConfigFile.get_project_description()
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
        python_versions = PyprojectConfigFile.get_supported_python_versions()
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
                rf"[![codecov]({get_codecov_url_from_git()}/branch/{DEFAULT_BRANCH}/graph/badge.svg)]({get_codecov_url_from_git()})",
                r"[![rumdl](https://img.shields.io/badge/markdown-rumdl-darkgreen)](https://github.com/rvben/rumdl)",
            ],
            "package-info": [
                rf"[![PyPI]({get_pypi_badge_url_from_git()})]({get_pypi_url_from_git()})",
                rf"[![Python](https://img.shields.io/badge/python-{joined_python_versions}-blue.svg?logo=python&logoColor=white)](https://www.python.org/)",
                rf"[![License]({get_licence_badge_url_from_git()})]({get_repo_url_from_git()}/blob/main/LICENSE)",
            ],
            "ci/cd": [
                rf"[![CI]({get_workflow_badge_url_from_git(health_check_wf_name, 'CI', 'github')})]({get_workflow_run_url_from_git(health_check_wf_name)})",  # noqa: E501
                rf"[![CD]({get_workflow_badge_url_from_git(release_wf_name, 'CD', 'github')})]({get_workflow_run_url_from_git(release_wf_name)})",  # noqa: E501
            ],
            "documentation": [
                rf"[![Documentation](https://img.shields.io/badge/Docs-GitHub%20Pages-black?style=for-the-badge&logo=github&logoColor=white)]({get_github_pages_url_from_git()})",
            ],
        }
