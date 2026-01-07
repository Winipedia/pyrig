"""Git version control wrapper.

Provides type-safe wrapper for Git commands: init, add, commit, push, tag, config.

Example:
    >>> from pyrig.dev.management.version_controller import VersionController
    >>> VersionController.L.get_add_all_args().run()
    >>> VersionController.L.get_commit_no_verify_args("Update docs").run()
    >>> VersionController.L.get_push_args().run()
"""

import logging
from functools import cache
from pathlib import Path
from urllib.parse import quote

from pyrig.dev.management.base.base import Tool
from pyrig.src.modules.package import get_project_name_from_cwd
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
        >>> VersionController.L.get_init_args().run()
        >>> VersionController.L.get_add_all_args().run()
        >>> VersionController.L.get_commit_no_verify_args("Initial commit").run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'git'
        """
        return "git"

    @classmethod
    def get_default_branch(cls) -> str:
        """Get the default branch name.

        Returns:
            Default branch name.
        """
        return "main"

    @classmethod
    def get_default_ruleset_name(cls) -> str:
        """Get the default branch protection ruleset name.

        Returns:
            Default ruleset name.
        """
        return f"{cls.get_default_branch()}-protection"

    @classmethod
    def get_init_args(cls, *args: str) -> Args:
        """Construct git init arguments.

        Args:
            *args: Init command arguments.

        Returns:
            Args for 'git init'.
        """
        return cls.get_args("init", *args)

    @classmethod
    def get_add_args(cls, *args: str) -> Args:
        """Construct git add arguments.

        Args:
            *args: Files or paths to add.

        Returns:
            Args for 'git add'.
        """
        return cls.get_args("add", *args)

    @classmethod
    def get_add_all_args(cls, *args: str) -> Args:
        """Construct git add arguments for all files.

        Args:
            *args: Add command arguments.

        Returns:
            Args for 'git add .'.
        """
        return cls.get_add_args(".", *args)

    @classmethod
    def get_add_pyproject_toml_args(cls, *args: str) -> Args:
        """Construct git add arguments for pyproject.toml.

        Args:
            *args: Add command arguments.

        Returns:
            Args for 'git add pyproject.toml'.
        """
        return cls.get_add_args("pyproject.toml", *args)

    @classmethod
    def get_add_pyproject_toml_and_lock_file_args(cls, *args: str) -> Args:
        """Construct git add arguments for pyproject.toml and uv.lock.

        Args:
            *args: Add command arguments.

        Returns:
            Args for 'git add pyproject.toml uv.lock'.
        """
        return cls.get_add_pyproject_toml_args("uv.lock", *args)

    @classmethod
    def get_commit_args(cls, *args: str) -> Args:
        """Construct git commit arguments.

        Args:
            *args: Commit command arguments.

        Returns:
            Args for 'git commit'.
        """
        return cls.get_args("commit", *args)

    @classmethod
    def get_commit_no_verify_args(cls, *args: str, msg: str) -> Args:
        """Construct git commit arguments with no verification.

        Args:
            *args: Commit command arguments.
            msg: Commit message.

        Returns:
            Args for 'git commit --no-verify -m <msg>'.
        """
        return cls.get_commit_args("--no-verify", "-m", msg, *args)

    @classmethod
    def get_push_args(cls, *args: str) -> Args:
        """Construct git push arguments.

        Args:
            *args: Push command arguments.

        Returns:
            Args for 'git push'.
        """
        return cls.get_args("push", *args)

    @classmethod
    def get_push_origin_args(cls, *args: str) -> Args:
        """Construct git push arguments for origin.

        Args:
            *args: Push command arguments.

        Returns:
            Args for 'git push origin'.
        """
        return cls.get_push_args("origin", *args)

    @classmethod
    def get_push_origin_tag_args(cls, *args: str, tag: str) -> Args:
        """Construct git push arguments for origin and tag.

        Args:
            *args: Push command arguments.
            tag: Tag name.

        Returns:
            Args for 'git push origin <tag>'.
        """
        return cls.get_push_origin_args(tag, *args)

    @classmethod
    def get_config_args(cls, *args: str) -> Args:
        """Construct git config arguments.

        Args:
            *args: Config command arguments.

        Returns:
            Args for 'git config'.
        """
        return cls.get_args("config", *args)

    @classmethod
    def get_config_global_args(cls, *args: str) -> Args:
        """Construct git config arguments with --global flag.

        Args:
            *args: Config command arguments.

        Returns:
            Args for 'git config --global'.
        """
        return cls.get_config_args("--global", *args)

    @classmethod
    def get_config_local_args(cls, *args: str) -> Args:
        """Construct git config arguments with --local flag.

        Args:
            *args: Config command arguments.

        Returns:
            Args for 'git config --local'.
        """
        return cls.get_config_args("--local", *args)

    @classmethod
    def get_config_local_user_email_args(cls, *args: str, email: str) -> Args:
        """Construct git config arguments for local user email.

        Args:
            *args: Config command arguments.
            email: Email address.

        Returns:
            Args for 'git config --local user.email <email>'.
        """
        return cls.get_config_local_args("user.email", email, *args)

    @classmethod
    def get_config_local_user_name_args(cls, *args: str, name: str) -> Args:
        """Construct git config arguments for local user name.

        Args:
            *args: Config command arguments.
            name: Name.

        Returns:
            Args for 'git config --local user.name <name>'.
        """
        return cls.get_config_local_args("user.name", name, *args)

    @classmethod
    def get_config_global_user_email_args(cls, *args: str, email: str) -> Args:
        """Construct git config arguments for global user email.

        Args:
            *args: Config command arguments.
            email: Email address.

        Returns:
            Args for 'git config --global user.email <email>'.
        """
        return cls.get_config_global_args("user.email", email, *args)

    @classmethod
    def get_config_global_user_name_args(cls, *args: str, name: str) -> Args:
        """Construct git config arguments for global user name.

        Args:
            *args: Config command arguments.
            name: Name.

        Returns:
            Args for 'git config --global user.name <name>'.
        """
        return cls.get_config_global_args("user.name", name, *args)

    @classmethod
    def get_tag_args(cls, *args: str, tag: str) -> Args:
        """Construct git tag arguments.

        Args:
            *args: Tag command arguments.
            tag: Tag name.

        Returns:
            Args for 'git tag'.
        """
        return cls.get_args("tag", tag, *args)

    @classmethod
    def get_config_get_args(cls, *args: str) -> Args:
        """Construct git config get arguments.

        Args:
            *args: Config get command arguments.

        Returns:
            Args for 'git config --get'.
        """
        return cls.get_config_args("--get", *args)

    @classmethod
    def get_config_get_remote_origin_url_args(cls, *args: str) -> Args:
        """Construct git config get remote origin URL arguments.

        Args:
            *args: Config get command arguments.

        Returns:
            Args for 'git config --get remote.origin.url'.
        """
        return cls.get_config_get_args("remote.origin.url", *args)

    @classmethod
    def get_config_get_user_name_args(cls, *args: str) -> Args:
        """Construct git config get user name arguments.

        Args:
            *args: Config get command arguments.

        Returns:
            Args for 'git config --get user.name'.
        """
        return cls.get_config_get_args("user.name", *args)

    @classmethod
    def get_diff_args(cls, *args: str) -> Args:
        """Construct git diff arguments.

        Args:
            *args: Diff command arguments.

        Returns:
            Args for 'git diff'.
        """
        return cls.get_args("diff", *args)

    @classmethod
    def get_diff_quiet_args(cls, *args: str) -> Args:
        """Construct git diff arguments with --quiet flag.

        Args:
            *args: Diff command arguments.

        Returns:
            Args for 'git diff --quiet'.
        """
        return cls.get_diff_args("--quiet", *args)

    @classmethod
    @cache
    def get_repo_owner_and_name(
        cls,
        *,
        check_repo_url: bool = True,
        url_encode: bool = False,
    ) -> tuple[str, str]:
        """Get the repository owner and name.

        Returns:
            Tuple of (owner, repository_name).
        """
        url = cls.get_repo_remote(check=check_repo_url)
        if not url:
            # we default to git username and repo name from cwd
            logger.debug(
                "No git remote found, using git username and CWD for repo info"
            )
            owner = cls.get_username()
            repo = get_project_name_from_cwd()
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
    def get_repo_remote(cls, *, check: bool = True) -> str:
        """Get the remote origin URL from git config.

        Args:
            check: Whether to raise exception if command fails.

        Returns:
            Remote origin URL (HTTPS or SSH format).
            Empty string if check=False and no remote.

        Raises:
            subprocess.CalledProcessError: If check=True and command fails.
        """
        args = cls.get_config_get_remote_origin_url_args()
        stdout = args.run(check=check).stdout
        return stdout.strip()

    @classmethod
    @cache
    def get_username(cls) -> str:
        """Get git username from local config.

        Returns:
            Configured git username (cached).

        Raises:
            subprocess.CalledProcessError: If user.name not configured.
        """
        args = cls.get_config_get_user_name_args()
        stdout = args.run().stdout
        return stdout.strip()

    @classmethod
    def has_unstaged_diff(cls) -> bool:
        """Check if there are any unstaged changes.

        Returns:
            True if there are unstaged changes.
        """
        args = cls.get_diff_quiet_args()
        completed_process = args.run(check=False)
        return completed_process.returncode != 0

    @classmethod
    def get_diff(cls) -> str:
        """Get the diff output.

        Returns:
            Diff output.
        """
        args = cls.get_diff_args()
        completed_process = args.run(check=False)
        return completed_process.stdout

    @classmethod
    def get_ignore_path(cls) -> Path:
        """Get the path to the .gitignore file.

        Returns:
            Path to .gitignore.
        """
        return Path(".gitignore")

    @classmethod
    def get_loaded_ignore(cls) -> list[str]:
        """Get the loaded gitignore patterns.

        Returns:
            List of gitignore patterns.
        """
        return cls.get_ignore_path().read_text(encoding="utf-8").splitlines()
