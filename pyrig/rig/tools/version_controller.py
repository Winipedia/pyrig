"""Git version control wrapper.

Provides type-safe wrapper for Git commands: init, add, commit, push, tag, config.

Example:
    >>> from pyrig.rig.tools.version_controller import VersionController
    >>> VersionController.I.add_all_args().run()
    >>> VersionController.I.commit_no_verify_args(msg="Update docs").run()
    >>> VersionController.I.push_args().run()
"""

import logging
from functools import cache
from pathlib import Path
from urllib.parse import quote

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.src.modules.package import project_name_from_cwd
from pyrig.src.processes import Args

logger = logging.getLogger(__name__)


class VersionController(Tool):
    """Git version control wrapper.

    Constructs git command arguments for version control operations.

    Operations:
        - Repository setup: init
        - Staging: add files, add all
        - Committing: commit with options
        - Remote operations: push, push tags
        - Tagging: create and push tags
        - Configuration: user name/email

    Example:
        >>> VersionController.I.init_args().run()
        >>> VersionController.I.add_all_args().run()
        >>> VersionController.I.commit_no_verify_args(msg="Initial commit").run()
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            'git'
        """
        return "git"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            `ToolGroup.TOOLING`
        """
        return ToolGroup.TOOLING

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge and linked page URLs."""
        return (
            "https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white",
            "https://git-scm.com",
        )

    def dev_dependencies(self) -> list[str]:
        """Get development dependencies.

        Returns:
            Empty list (git is a system dependency).
        """
        # git is a system dependency, so we don't have a dev dependency for it
        return []

    def default_branch(self) -> str:
        """Get the default branch name.

        Returns:
            Default branch name.
        """
        return "main"

    def ignore_filename(self) -> str:
        """Get the filename for .gitignore.

        Returns:
            Filename for .gitignore.
        """
        return ".gitignore"

    def default_ruleset_name(self) -> str:
        """Get the default branch protection ruleset name.

        Returns:
            Default ruleset name.
        """
        return f"{self.default_branch()}-protection"

    def init_args(self, *args: str) -> Args:
        """Construct git init arguments.

        Args:
            *args: Init command arguments.

        Returns:
            Args for 'git init'.
        """
        return self.args("init", *args)

    def add_args(self, *args: str) -> Args:
        """Construct git add arguments.

        Args:
            *args: Files or paths to add.

        Returns:
            Args for 'git add'.
        """
        return self.args("add", *args)

    def add_all_args(self, *args: str) -> Args:
        """Construct git add arguments for all files.

        Args:
            *args: Add command arguments.

        Returns:
            Args for 'git add .'.
        """
        return self.add_args(".", *args)

    def add_pyproject_toml_args(self, *args: str) -> Args:
        """Construct git add arguments for pyproject.toml.

        Args:
            *args: Add command arguments.

        Returns:
            Args for 'git add pyproject.toml'.
        """
        return self.add_args("pyproject.toml", *args)

    def add_pyproject_toml_and_lock_file_args(self, *args: str) -> Args:
        """Construct git add arguments for pyproject.toml and uv.lock.

        Args:
            *args: Add command arguments.

        Returns:
            Args for 'git add pyproject.toml uv.lock'.
        """
        return self.add_pyproject_toml_args("uv.lock", *args)

    def commit_args(self, *args: str) -> Args:
        """Construct git commit arguments.

        Args:
            *args: Commit command arguments.

        Returns:
            Args for 'git commit'.
        """
        return self.args("commit", *args)

    def commit_no_verify_args(self, *args: str, msg: str) -> Args:
        """Construct git commit arguments with no verification.

        Args:
            *args: Commit command arguments.
            msg: Commit message.

        Returns:
            Args for 'git commit --no-verify -m <msg>'.
        """
        return self.commit_args("--no-verify", "-m", msg, *args)

    def push_args(self, *args: str) -> Args:
        """Construct git push arguments.

        Args:
            *args: Push command arguments.

        Returns:
            Args for 'git push'.
        """
        return self.args("push", *args)

    def push_origin_args(self, *args: str) -> Args:
        """Construct git push arguments for origin.

        Args:
            *args: Push command arguments.

        Returns:
            Args for 'git push origin'.
        """
        return self.push_args("origin", *args)

    def push_origin_tag_args(self, *args: str, tag: str) -> Args:
        """Construct git push arguments for origin and tag.

        Args:
            *args: Push command arguments.
            tag: Tag name.

        Returns:
            Args for 'git push origin <tag>'.
        """
        return self.push_origin_args(tag, *args)

    def config_args(self, *args: str) -> Args:
        """Construct git config arguments.

        Args:
            *args: Config command arguments.

        Returns:
            Args for 'git config'.
        """
        return self.args("config", *args)

    def config_global_args(self, *args: str) -> Args:
        """Construct git config arguments with --global flag.

        Args:
            *args: Config command arguments.

        Returns:
            Args for 'git config --global'.
        """
        return self.config_args("--global", *args)

    def config_local_args(self, *args: str) -> Args:
        """Construct git config arguments with --local flag.

        Args:
            *args: Config command arguments.

        Returns:
            Args for 'git config --local'.
        """
        return self.config_args("--local", *args)

    def config_local_user_email_args(self, *args: str, email: str) -> Args:
        """Construct git config arguments for local user email.

        Args:
            *args: Config command arguments.
            email: Email address.

        Returns:
            Args for 'git config --local user.email <email>'.
        """
        return self.config_local_args("user.email", email, *args)

    def config_local_user_name_args(self, *args: str, name: str) -> Args:
        """Construct git config arguments for local user name.

        Args:
            *args: Config command arguments.
            name: Name.

        Returns:
            Args for 'git config --local user.name <name>'.
        """
        return self.config_local_args("user.name", name, *args)

    def config_global_user_email_args(self, *args: str, email: str) -> Args:
        """Construct git config arguments for global user email.

        Args:
            *args: Config command arguments.
            email: Email address.

        Returns:
            Args for 'git config --global user.email <email>'.
        """
        return self.config_global_args("user.email", email, *args)

    def config_global_user_name_args(self, *args: str, name: str) -> Args:
        """Construct git config arguments for global user name.

        Args:
            *args: Config command arguments.
            name: Name.

        Returns:
            Args for 'git config --global user.name <name>'.
        """
        return self.config_global_args("user.name", name, *args)

    def tag_args(self, *args: str, tag: str) -> Args:
        """Construct git tag arguments.

        Args:
            *args: Tag command arguments.
            tag: Tag name.

        Returns:
            Args for 'git tag <tag>'.
        """
        return self.args("tag", tag, *args)

    def config_get_args(self, *args: str) -> Args:
        """Construct git config get arguments.

        Args:
            *args: Config get command arguments.

        Returns:
            Args for 'git config --get'.
        """
        return self.config_args("--get", *args)

    def config_remote_origin_url_args(self, *args: str) -> Args:
        """Construct git config get remote origin URL arguments.

        Args:
            *args: Config get command arguments.

        Returns:
            Args for 'git config --get remote.origin.url'.
        """
        return self.config_get_args("remote.origin.url", *args)

    def config_get_user_name_args(self, *args: str) -> Args:
        """Construct git config get user name arguments.

        Args:
            *args: Config get command arguments.

        Returns:
            Args for 'git config --get user.name'.
        """
        return self.config_get_args("user.name", *args)

    def config_get_user_email_args(self, *args: str) -> Args:
        """Construct git config get user email arguments.

        Args:
            *args: Config get command arguments.

        Returns:
            Args for 'git config --get user.email'.
        """
        return self.config_get_args("user.email", *args)

    def diff_args(self, *args: str) -> Args:
        """Construct git diff arguments.

        Args:
            *args: Diff command arguments.

        Returns:
            Args for 'git diff'.
        """
        return self.args("diff", *args)

    def diff_quiet_args(self, *args: str) -> Args:
        """Construct git diff arguments with --quiet flag.

        Args:
            *args: Diff command arguments.

        Returns:
            Args for 'git diff --quiet'.
        """
        return self.diff_args("--quiet", *args)

    def _repo_owner_and_name(
        self,
        *,
        check_repo_url: bool = True,
        url_encode: bool = False,
    ) -> tuple[str, str]:
        """Get the repository owner and name.

        Parses the git remote origin URL to extract owner and repo name.
        Falls back to the git username and current working directory name
        if no remote is configured.

        Args:
            check_repo_url: Whether to raise on missing remote. Defaults to True.
            url_encode: Whether to percent-encode the returned strings.
                Defaults to False.

        Returns:
            Tuple of (owner, repository_name).
        """
        url = self.repo_remote(check=check_repo_url)
        if not url:
            # we default to git username and repo name from cwd
            logger.debug(
                "No git remote found, using git username and CWD for repo info"
            )
            owner = self.username()
            repo = project_name_from_cwd()
            logger.debug("Derived repository: %s/%s", owner, repo)
        else:
            parts = url.removesuffix(".git").split("/")
            # keep last two parts
            owner, repo = parts[-2:]
            if ":" in owner:
                owner = owner.split(":")[-1]
        if url_encode:
            logger.debug("Url encoding owner and repo")
            owner = quote(owner)
            repo = quote(repo)
        return owner, repo

    @classmethod
    @cache
    def repo_owner_and_name(
        cls, *, check_repo_url: bool = True, url_encode: bool = False
    ) -> tuple[str, str]:
        """Get the repository owner and name.

        Wrapper around the instance method _repo_owner_and_name
        to allow caching at the class level.

        The user should override the instance method _repo_owner_and_name
        for the actual logic, and this class method will handle caching and
        provide a convenient interface.

        Args:
            check_repo_url: Whether to raise on missing remote. Defaults to True.
            url_encode: Whether to percent-encode the returned strings.
                Defaults to False.

        Returns:
            Tuple of (owner, repository_name).
        """
        return cls()._repo_owner_and_name(  # noqa: SLF001
            check_repo_url=check_repo_url, url_encode=url_encode
        )

    def repo_remote(self, *, check: bool = True) -> str:
        """Get the remote origin URL from git config.

        Args:
            check: Whether to raise exception if command fails.

        Returns:
            Remote origin URL (HTTPS or SSH format).
            Empty string if check=False and no remote.

        Raises:
            subprocess.CalledProcessError: If check=True and command fails.
        """
        args = self.config_remote_origin_url_args()
        stdout = args.run_cached(check=check).stdout
        return stdout.strip()

    def username(self) -> str:
        """Get git username from config.

        Returns:
            Configured git username.

        Raises:
            subprocess.CalledProcessError: If user.name not configured.
        """
        args = self.config_get_user_name_args()
        stdout = args.run_cached().stdout
        return stdout.strip()

    def has_unstaged_diff(self) -> bool:
        """Check if there are any unstaged changes.

        Returns:
            True if there are unstaged changes.
        """
        args = self.diff_quiet_args()
        completed_process = args.run(check=False)
        return completed_process.returncode != 0

    def diff(self) -> str:
        """Get the diff output.

        Returns:
            Diff output.
        """
        args = self.diff_args()
        completed_process = args.run(check=False)
        return completed_process.stdout

    def ignore_path(self) -> Path:
        """Get the path to the .gitignore file.

        Returns:
            Path to .gitignore.
        """
        return Path(self.ignore_filename())

    def loaded_ignore(self) -> list[str]:
        """Get the loaded gitignore patterns.

        Returns:
            List of gitignore patterns.
        """
        return self.ignore_path().read_text(encoding="utf-8").splitlines()

    def email(self) -> str:
        """Get the email from git config.

        Returns:
            Email.
        """
        args = self.config_get_user_email_args()
        stdout = args.run_cached().stdout
        return stdout.strip()
