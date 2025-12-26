"""Configuration management for Markdown files that contain badges.

This module provides the BadgesMarkdownConfigFile class for creating and
managing Markdown files that contain badges.
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
    """Abstract base class for Markdown configuration files that contain badges.

    Attributes:
        CONTENT_KEY: Dictionary key used to store file content.
    """

    @classmethod
    def get_content_str(cls) -> str:
        """Generate the README content with project header.

        Returns:
            Markdown content with project name and optional pyrig reference.
        """
        project_name = PyprojectConfigFile.get_project_name()
        badges = cls.get_badges()
        badges_str = ""
        for badge_category, badge_list in badges.items():
            badges_str += f"<!-- {badge_category} -->\n"
            badges_str += "\n".join(badge_list) + "\n"
        badges_str = badges_str.removesuffix("\n")
        description = PyprojectConfigFile.get_project_description()
        return f"""# {project_name}

{badges_str}

---

> {description}

---
"""

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the README.md file is valid.

        Returns:
            True if the file has required structure.
        """
        file_content = cls.get_file_content()
        badges = [
            badge for _group, badges in cls.get_badges().items() for badge in badges
        ]
        all_badges_in_file = all(badge in file_content for badge in badges)
        description_in_file = (
            PyprojectConfigFile.get_project_description() in file_content
        )
        project_name_in_file = PyprojectConfigFile.get_project_name() in file_content
        return super().is_correct() or (
            all_badges_in_file and description_in_file and project_name_in_file
        )

    @classmethod
    def get_badges(cls) -> dict[str, list[str]]:
        """Get the badges for the README.md file.

        Returns:
            List of badge markdown strings.
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
