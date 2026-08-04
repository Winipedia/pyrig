"""Configuration management for CONTRIBUTING.md files.

Manages CONTRIBUTING.md using a template covering the code of conduct,
how to report bugs and suggest features, the development workflow, and
pull request expectations.
"""

from pathlib import Path

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.hooks.manager import (
    VersionControlHookManager,
)
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class ContributingConfigFile(MarkdownConfigFile):
    """Configuration manager for the project's CONTRIBUTING.md file.

    Generates CONTRIBUTING.md covering the code of conduct, how to report
    bugs and suggest features, the development workflow, and pull request
    expectations. Commands and remote URLs are derived from the project's
    own tool and configuration classes, so nothing is left for downstream
    users to fill in by hand. Users are free to customize the file after
    initial generation.
    """

    def content(self) -> str:
        """Return the complete contributing guide text.

        Returns:
            The welcome message, security notice, code of conduct, ways to
            contribute, development workflow, and pull request sections
            joined into a single Markdown document.
        """
        return f"""# Contributing

{self.welcome_section()}

{self.security_notice_section()}

{self.code_of_conduct_section()}

{self.ways_to_contribute_section()}

{self.development_workflow_section()}

{self.pull_request_section()}
"""

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `"CONTRIBUTING"` as the filename stem."""
        return "CONTRIBUTING"

    def welcome_section(self) -> str:
        """Return the opening welcome paragraph.

        Returns:
            A paragraph, addressed to the project by name, thanking the
            reader and explaining why following the guide matters.
        """
        project_name = PackageManager.I.project_name()
        return f"""Thanks for considering a contribution to {project_name}! Following
these guidelines respects the time of the people who maintain and review
this project, and helps them address your issue or pull request quickly."""

    def security_notice_section(self) -> str:
        """Return the security-vulnerability callout.

        Points to `SECURITY.md` instead of restating its reporting
        process, so the two files can't drift out of sync.

        Returns:
            A blockquote directing security reports toward `SECURITY.md`.
        """
        return """> **Found a security vulnerability?**
> Please follow [SECURITY.md](SECURITY.md)."""

    def code_of_conduct_section(self) -> str:
        """Return the code-of-conduct section.

        Returns:
            The `## Code of Conduct` section, linking to
            `CODE_OF_CONDUCT.md` rather than restating it.
        """
        return """## Code of Conduct

By participating in this project, you agree to abide by its
[Code of Conduct](CODE_OF_CONDUCT.md)."""

    def ways_to_contribute_section(self) -> str:
        """Return the section describing how to report issues and ideas.

        Returns:
            The `## Ways to Contribute` section, linking to the project's
            issue tracker and describing what a good bug report, feature
            request, and question look like.
        """
        issues_url = RemoteVersionController.I.issues_url()
        return f"""## Ways to Contribute

Contributions aren't limited to code — reporting bugs, improving
documentation, and answering questions are just as valuable. Before
opening a new issue, search [existing issues]({issues_url})
to avoid duplicates.

- **Bugs** — describe what you expected, what happened instead, and the
  steps to reproduce it.
- **Features** — describe the problem before proposing a solution, and
  open an issue before starting a large pull request so the approach can
  be discussed first.
- **Questions** — open an issue if nothing else already answers it."""

    def development_workflow_section(self) -> str:
        """Return the section walking through how to submit a change.

        Every command is built from the project's own `Tool` classes
        rather than written out by hand, so it can never drift from what
        the project actually runs.

        Returns:
            The `## Development Workflow` section, as a numbered list.
        """
        install_cmd = PackageManager.I.install_dependencies_args()
        hooks_install_cmd = PackageManager.I.run_args(
            *VersionControlHookManager.I.install_args(),
        )
        return f"""## Development Workflow

1. Fork and clone the repository.
2. Install the dependencies: `{install_cmd}`
3. Install the git hooks: `{hooks_install_cmd}`
4. Create a branch for your change.
5. Make your change.
6. Commit your change.
7. Push your branch and open a pull request."""

    def pull_request_section(self) -> str:
        """Return the section describing what a mergeable pull request needs.

        Returns:
            The `## Pull Requests` section, with the CI link derived from
            the project's own configuration.
        """
        cicd_url = RemoteVersionController.I.cicd_url(
            HealthCheckWorkflowConfigFile.I.stem(),
        )
        return f"""## Pull Requests

- Reference related issues in the description.
- Keep changes focused and atomic.
- Update documentation.
- All checks in [CI]({cicd_url}) must pass before merge."""
