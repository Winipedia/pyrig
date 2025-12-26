"""Configuration management for Markdown files that contain badges.

This module provides the BadgesMarkdownConfigFile class for creating and
managing Markdown files that contain project badges (README.md, etc.).

BadgesMarkdownConfigFile automatically generates:
- Project header with name and description
- Categorized badges (tooling, code quality, package info, CI/CD, docs)
- Links to project resources (PyPI, GitHub, documentation)

The badges are dynamically generated from:
- Project metadata in pyproject.toml
- Git repository information
- Workflow configurations
- Python version support

Badge Categories:
    - **Tooling**: pyrig, uv, Podman, pre-commit, MkDocs
    - **Code Quality**: ruff, ty, bandit, pytest, codecov, rumdl
    - **Package Info**: PyPI version, Python versions, license
    - **CI/CD**: Health check workflow, release workflow
    - **Documentation**: GitHub Pages link

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
    >>> ReadmeFile()
    # Creates README.md with project header, badges, and description
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
    """Abstract base class for Markdown files that contain project badges.

    Extends MarkdownConfigFile to automatically generate project badges from
    metadata in pyproject.toml and Git repository information. The generated
    content includes:

    - Project name as H1 header
    - Categorized badges (tooling, code quality, package info, CI/CD, docs)
    - Project description
    - Horizontal rules for visual separation

    The badges are organized into categories with HTML comments for clarity:
    - <!-- tooling -->: Development tools (pyrig, uv, Podman, etc.)
    - <!-- code-quality -->: Quality tools (ruff, ty, bandit, pytest, etc.)
    - <!-- package-info -->: Package metadata (PyPI, Python versions, license)
    - <!-- ci/cd -->: CI/CD workflows (health check, release)
    - <!-- documentation -->: Documentation links (GitHub Pages)

    Validation Behavior:
        A file is considered correct if it contains:
        - All badges from get_badges()
        - The project description from pyproject.toml
        - The project name from pyproject.toml

        This allows users to add extra content while ensuring required
        elements are present.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the Markdown file

    Example:
        >>> from pathlib import Path
        >>> from pyrig.dev.configs.base.badges_md import BadgesMarkdownConfigFile
        >>>
        >>> class ReadmeFile(BadgesMarkdownConfigFile):
        ...     @classmethod
        ...     def get_parent_path(cls) -> Path:
        ...         return Path()

    See Also:
        pyrig.dev.configs.base.markdown.MarkdownConfigFile: Parent class
        pyrig.dev.configs.pyproject.PyprojectConfigFile: Project metadata
        pyrig.src.git: Git repository utilities
    """

    @classmethod
    def get_content_str(cls) -> str:
        """Generate the Markdown content with project header and badges.

        Creates a formatted Markdown document with:
        1. Project name as H1 header
        2. Categorized badges with HTML comments
        3. Horizontal rule separator
        4. Project description as blockquote
        5. Horizontal rule separator

        The badges are organized by category with HTML comments for clarity:
        - <!-- tooling -->: Development tools
        - <!-- code-quality -->: Quality tools
        - <!-- package-info -->: Package metadata
        - <!-- ci/cd -->: CI/CD workflows
        - <!-- documentation -->: Documentation links

        Returns:
            Markdown content with project name, badges, and description.

        Example:
            Generated content::

                # MyProject

                <!-- tooling -->
                [![pyrig](...)][...]
                [![uv](...)][...]

                <!-- code-quality -->
                [![ruff](...)][...]
                [![pytest](...)][...]

                <!-- package-info -->
                [![PyPI](...)][...]

                <!-- ci/cd -->
                [![CI](...)][...]

                <!-- documentation -->
                [![Documentation](...)][...]

                ---

                > Project description goes here.

                ---

        Note:
            The badges are generated dynamically from get_badges() and may
            vary based on project configuration.
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
        r"""Check if the Markdown file contains required badges and content.

        Validates that the file contains:
        1. All badges from get_badges() (across all categories)
        2. The project description from pyproject.toml
        3. The project name from pyproject.toml

        This validation is more lenient than exact content matching, allowing
        users to add extra content while ensuring required elements are present.

        Returns:
            True if the file is empty (opted out), has exact match, or contains
            all required badges, description, and project name.

        Example:
            Valid files::

                # Empty file (opted out)
                ""

                # Exact match (from get_content_str())
                "# MyProject\n\n[![badge]...]\n\n---\n\n> Description\n\n---\n"

                # Has all required elements + extra content
                "# MyProject\n\n[![badge]...]\n\n> Description\n\n## Extra\n"

            Invalid files::

                # Missing badges
                "# MyProject\n\n> Description\n"

                # Missing description
                "# MyProject\n\n[![badge]...]\n"

                # Missing project name
                "[![badge]...]\n\n> Description\n"

        Note:
            The validation checks for presence, not exact formatting. Users can
            reorder or add content as long as required elements are present.
        """
        file_content = cls.get_file_content()
        badges = [
            badge for _, badge_list in cls.get_badges().items() for badge in badge_list
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
        """Get categorized badges for the Markdown file.

        Generates a dictionary of badge categories, each containing a list of
        Markdown badge strings. The badges are dynamically generated from:
        - Project metadata in pyproject.toml
        - Git repository information
        - Workflow configurations
        - Python version support

        Badge Categories:
            - **tooling**: Development tools (pyrig, uv, Podman, pre-commit, MkDocs)
            - **code-quality**: Quality tools (ruff, ty, bandit, pytest, codecov, rumdl)
            - **package-info**: Package metadata (PyPI, Python versions, license)
            - **ci/cd**: CI/CD workflows (health check, release)
            - **documentation**: Documentation links (GitHub Pages)

        Returns:
            Dictionary mapping category names to lists of badge Markdown strings.
            Each badge is a Markdown link with an embedded image.

        Example:
            Get badges::

                badges = cls.get_badges()
                # Returns:
                # {
                #     "tooling": [
                #         "[![pyrig](...)](...)",
                #         "[![uv](...)](...)",
                #         ...
                #     ],
                #     "code-quality": [
                #         "[![ruff](...)](...)",
                #         ...
                #     ],
                #     ...
                # }

            Use in content generation::

                for category, badge_list in badges.items():
                    print(f"<!-- {category} -->")
                    for badge in badge_list:
                        print(badge)

        Note:
            The badges use shields.io for consistent styling and include
            dynamic information like Python versions and workflow status.
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
