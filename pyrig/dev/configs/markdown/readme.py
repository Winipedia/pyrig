"""Configuration management for README.md files.

This module provides the ReadmeConfigFile class for creating and
managing the project's README.md file with a standard header.
"""

from pathlib import Path

import pyrig
from pyrig.dev.cli.utils.repo import DEFAULT_BRANCH
from pyrig.dev.configs.base.base import MarkdownConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.git.git import get_repo_owner_and_name_from_git


class ReadmeConfigFile(MarkdownConfigFile):
    """Configuration file manager for README.md.

    Creates a README.md file with the project name as a header.
    For projects using pyrig, includes a reference link to pyrig.
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the README filename.

        Returns:
            The string "README".
        """
        return "README"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the project root directory.

        Returns:
            Path to the project root.
        """
        return Path()

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
        description = PyprojectConfigFile.get_project_description()
        return f"""# {project_name}

{badges_str}

---

> {description}

---
"""

    @classmethod
    def is_unwanted(cls) -> bool:
        """Check if README is unwanted (always False).

        Returns:
            False, as README.md is always required.
        """
        # README.md is never unwanted
        return False

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the README.md file is valid.

        Returns:
            True if the file has required structure.
        """
        badges = cls.get_badges()
        all_badges_in_file = all(badge in cls.get_file_content() for badge in badges)
        description_in_file = (
            PyprojectConfigFile.get_project_description() in cls.get_file_content()
        )
        project_name_in_file = (
            PyprojectConfigFile.get_project_name() in cls.get_file_content()
        )
        return super().is_correct() or (
            all_badges_in_file and description_in_file and project_name_in_file
        )

    @classmethod
    def get_badges(cls) -> dict[str, list[str]]:
        """Get the badges for the README.md file.

        Returns:
            List of badge markdown strings.
        """
        repo_owner, repo_name = get_repo_owner_and_name_from_git(check_repo_url=False)
        project_name = PyprojectConfigFile.get_project_name()
        python_versions = PyprojectConfigFile.get_supported_python_versions()
        joined_python_versions = "|".join(str(v) for v in python_versions)
        return {
            "tooling": [
                f"[![{pyrig.__name__}](https://img.shields.io/badge/built%20with-{pyrig.__name__}-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/{pyrig.__name__})",
                "[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)",
                "[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)",
            ],
            "code-quality": [
                "[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)",
                "[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)"
                "[![mypy](https://img.shields.io/badge/type%20checked-mypy-039dfc.svg)](https://mypy-lang.org/)",
                "[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)",
                "[![pytest](https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest)](https://pytest.org/)",
                f"[![codecov](https://codecov.io/gh/{repo_owner}/{repo_name}/branch/{DEFAULT_BRANCH}/graph/badge.svg)](https://codecov.io/gh/{repo_owner}/{repo_name})",
            ],
            "package-info": [
                f"[![PyPI](https://img.shields.io/pypi/v/{project_name}?logo=pypi&logoColor=white)](https://pypi.org/project/{project_name}/)",
                f"[![Python](https://img.shields.io/badge/python-{joined_python_versions}-blue.svg?logo=python&logoColor=white)](https://www.python.org/)",
                f"[![License](https://img.shields.io/github/license/{repo_owner}/{repo_name})](https://github.com/{repo_owner}/{repo_name}/blob/main/LICENSE)",
            ],
            "ci/cd": [
                f"[![CI](https://img.shields.io/github/actions/workflow/status/{repo_owner}/{repo_name}/health_check.yaml?label=CI&logo=github)](https://github.com/{repo_owner}/{repo_name}/actions/workflows/health_check.yaml)",
                f"[![CD](https://img.shields.io/github/actions/workflow/status/{repo_owner}/{repo_name}/release.yaml?label=CD&logo=github)](https://github.com/{repo_owner}/{repo_name}/actions/workflows/release.yaml)",
            ],
        }
