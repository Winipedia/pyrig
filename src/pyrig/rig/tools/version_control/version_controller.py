"""Version controller wrapper.

Wraps VersionController commands and information.
"""

import logging
from functools import cache
from urllib.parse import quote

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup
from pyrig.rig.tools.package_manager import PackageManager

logger = logging.getLogger(__name__)


class VersionController(Tool):
    """Type-safe git command argument builder.

    Each method constructs an ``Args`` object representing a specific git
    command.  ``Args`` objects can be executed directly via ``.run()`` or
    converted to a string for embedding in shell scripts and workflow files.
    All commands are automatically prefixed with ``git``.

    Example:
        >>> VersionController.I.init_args().run()
        >>> VersionController.I.add_all_args().run()
        >>> VersionController.I.commit_no_verify_args(msg="Initial commit").run()
    """

    def name(self) -> str:
        """Return the tool's command name.

        Returns:
            ``'git'``
        """
        return "git"

    def group(self) -> str:
        """Return the badge group this tool belongs to.

        Returns:
            ``ToolGroup.TOOLING``
        """
        return ToolGroup.TOOLING

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge image URL and its linked page URL for Git.

        Returns:
            A ``(badge_url, page_url)`` tuple of strings.
        """
        return (
            "https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white",
            "https://git-scm.com",
        )

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return development dependencies for this tool.

        Git is a system dependency installed outside the Python environment,
        so no pip-installable package is needed here.

        Returns:
            An empty tuple.
        """
        # git is a system dependency, so we don't have a dev dependency for it
        return ()

    # -------------------------------------------------------------------------
    # Tool constants
    # -------------------------------------------------------------------------

    def default_branch(self) -> str:
        """Return the default branch name for new repositories.

        Returns:
            ``'main'``
        """
        return "main"

    def default_ruleset_name(self) -> str:
        """Return the default branch-protection ruleset name.

        The name follows the convention ``<branch>-protection``, derived from
        ``default_branch()``.  For example, if the default branch is ``main``
        the ruleset name is ``main-protection``.

        Returns:
            The default branch-protection ruleset name string.
        """
        return f"{self.default_branch()}-protection"

    # -------------------------------------------------------------------------
    # Repository initialisation
    # -------------------------------------------------------------------------

    def init_args(self, *args: str) -> Args:
        """Build arguments for ``git init``.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git init [args]``.
        """
        return self.args("init", *args)

    # -------------------------------------------------------------------------
    # Staging
    # -------------------------------------------------------------------------

    def add_pyproject_toml_and_lock_file_args(self, *args: str) -> Args:
        """Build arguments to stage ``pyproject.toml`` and ``uv.lock`` together.

        Used in CI workflow steps that bump the project version or sync
        dependencies so that both the manifest and the lock file are always
        committed as a pair.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git add pyproject.toml uv.lock [args]``.
        """
        return self.add_pyproject_toml_args("uv.lock", *args)

    def add_all_args(self, *args: str) -> Args:
        """Build arguments to stage all modified and untracked files.

        Equivalent to running ``git add .`` from the current working directory.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git add . [args]``.
        """
        return self.add_args(".", *args)

    def add_pyproject_toml_args(self, *args: str) -> Args:
        """Build arguments to stage ``pyproject.toml``.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git add pyproject.toml [args]``.
        """
        return self.add_args("pyproject.toml", *args)

    def add_args(self, *args: str) -> Args:
        """Build base arguments for ``git add``.

        Args:
            *args: Files or paths to stage.

        Returns:
            Args for ``git add [args]``.
        """
        return self.args("add", *args)

    # -------------------------------------------------------------------------
    # Committing
    # -------------------------------------------------------------------------

    def commit_no_verify_args(self, *args: str, msg: str) -> Args:
        """Build arguments for ``git commit --no-verify -m <msg>``.

        The ``--no-verify`` flag bypasses all pre-commit and commit-msg hooks.
        This is intentional in automated CI steps where running hooks would
        either re-trigger expensive checks or cause recursive hook invocations.

        Args:
            *args: Additional arguments appended to the command.
            msg: The commit message.

        Returns:
            Args for ``git commit --no-verify -m <msg> [args]``.
        """
        return self.commit_args("--no-verify", "-m", msg, *args)

    def commit_args(self, *args: str) -> Args:
        """Build base arguments for ``git commit``.

        Args:
            *args: Commit options or message flags (e.g. ``-m``, ``--amend``).

        Returns:
            Args for ``git commit [args]``.
        """
        return self.args("commit", *args)

    # -------------------------------------------------------------------------
    # Pushing
    # -------------------------------------------------------------------------

    def push_no_verify_origin_tag_args(self, *args: str, tag: str) -> Args:
        """Build arguments to push a specific tag to the ``origin`` remote.

        Used in release workflows to publish a version tag immediately after
        it has been created locally.
        The ``--no-verify`` flag bypasses all pre-push hooks.  This is
        intentional in automated CI steps where running hooks would either
        re-trigger expensive checks or cause recursive hook invocations.

        Args:
            *args: Additional arguments appended to the command.
            tag: The tag ref to push (e.g. ``v1.2.3``).

        Returns:
            Args for ``git push origin <tag> [args]``.
        """
        return self.push_no_verify_origin_args(tag, *args)

    def push_no_verify_origin_args(self, *args: str) -> Args:
        """Build arguments for ``git push origin --no-verify``.

        The ``--no-verify`` flag bypasses all pre-push hooks.  This is
        intentional in automated CI steps where running hooks would either
        re-trigger expensive checks or cause recursive hook invocations.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git push origin --no-verify [args]``.
        """
        return self.push_no_verify_args("origin", *args)

    def push_no_verify_args(self, *args: str) -> Args:
        """Build arguments for ``git push --no-verify``.

        The ``--no-verify`` flag bypasses all pre-push hooks.  This is
        intentional in automated CI steps where running hooks would either
        re-trigger expensive checks or cause recursive hook invocations.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git push --no-verify [args]``.
        """
        return self.push_args("--no-verify", *args)

    def push_args(self, *args: str) -> Args:
        """Build base arguments for ``git push``.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git push [args]``.
        """
        return self.args("push", *args)

    # -------------------------------------------------------------------------
    # Tagging
    # -------------------------------------------------------------------------

    def tag_args(self, *args: str, tag: str) -> Args:
        """Build arguments to create a local tag.

        Args:
            *args: Additional arguments appended to the command.
            tag: The tag name to create (e.g. ``v1.2.3``).

        Returns:
            Args for ``git tag <tag> [args]``.
        """
        return self.args("tag", tag, *args)

    # -------------------------------------------------------------------------
    # Configuration - write/set
    # -------------------------------------------------------------------------

    def config_local_user_email_args(self, *args: str, email: str) -> Args:
        """Build arguments to set the local repository user email.

        Args:
            *args: Additional arguments appended to the command.
            email: The email address to configure.

        Returns:
            Args for ``git config --local user.email <email> [args]``.
        """
        return self.config_local_args("user.email", email, *args)

    def config_local_user_name_args(self, *args: str, name: str) -> Args:
        """Build arguments to set the local repository user name.

        Args:
            *args: Additional arguments appended to the command.
            name: The user name to configure.

        Returns:
            Args for ``git config --local user.name <name> [args]``.
        """
        return self.config_local_args("user.name", name, *args)

    def config_global_user_email_args(self, *args: str, email: str) -> Args:
        """Build arguments to set the global user email.

        Args:
            *args: Additional arguments appended to the command.
            email: The email address to configure.

        Returns:
            Args for ``git config --global user.email <email> [args]``.
        """
        return self.config_global_args("user.email", email, *args)

    def config_global_user_name_args(self, *args: str, name: str) -> Args:
        """Build arguments to set the global user name.

        Args:
            *args: Additional arguments appended to the command.
            name: The user name to configure.

        Returns:
            Args for ``git config --global user.name <name> [args]``.
        """
        return self.config_global_args("user.name", name, *args)

    def config_local_args(self, *args: str) -> Args:
        """Build arguments for ``git config --local``.

        Local scope means changes apply only to the current repository and do
        not affect the user's global git configuration.

        Args:
            *args: Configuration key/value pairs or additional flags.

        Returns:
            Args for ``git config --local [args]``.
        """
        return self.config_args("--local", *args)

    def config_global_args(self, *args: str) -> Args:
        """Build arguments for ``git config --global``.

        Global scope means changes apply to the current user's git configuration
        across all repositories on the machine.

        Args:
            *args: Configuration key/value pairs or additional flags.

        Returns:
            Args for ``git config --global [args]``.
        """
        return self.config_args("--global", *args)

    # -------------------------------------------------------------------------
    # Configuration - read/get
    # -------------------------------------------------------------------------

    def config_remote_origin_url_args(self, *args: str) -> Args:
        """Build arguments to read the ``remote.origin.url`` value.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git config --get remote.origin.url [args]``.
        """
        return self.config_get_args("remote.origin.url", *args)

    def config_get_user_name_args(self, *args: str) -> Args:
        """Build arguments to read the configured ``user.name`` value.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git config --get user.name [args]``.
        """
        return self.config_get_args("user.name", *args)

    def config_get_user_email_args(self, *args: str) -> Args:
        """Build arguments to read the configured ``user.email`` value.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git config --get user.email [args]``.
        """
        return self.config_get_args("user.email", *args)

    def config_get_args(self, *args: str) -> Args:
        """Build base arguments for ``git config --get``.

        The ``--get`` flag instructs git to print the value for the given key
        and exit with a non-zero code when the key is absent.

        Args:
            *args: The configuration key to query.

        Returns:
            Args for ``git config --get [args]``.
        """
        return self.config_args("--get", *args)

    # -------------------------------------------------------------------------
    # Configuration - base
    # -------------------------------------------------------------------------

    def config_args(self, *args: str) -> Args:
        """Build base arguments for ``git config``.

        Args:
            *args: Config subcommands, scope flags, and key/value pairs.

        Returns:
            Args for ``git config [args]``.
        """
        return self.args("config", *args)

    # -------------------------------------------------------------------------
    # Diff
    # -------------------------------------------------------------------------

    def has_unstaged_diff(self) -> bool:
        """Check whether the working tree contains any unstaged changes.

        Runs ``git diff --quiet``, which exits with code ``0`` when the working
        tree is clean and with a non-zero code when uncommitted differences
        exist.  The exit code is used rather than parsing output, making this
        check fast and reliable.

        Returns:
            ``True`` if there are unstaged changes, ``False`` if the working
            tree is clean.
        """
        args = self.diff_quiet_args()
        completed_process = args.run(check=False)
        return completed_process.returncode != 0

    def diff(self) -> str:
        """Return the current unstaged diff as a string.

        Returns:
            The raw output of ``git diff``, or an empty string when the
            working tree is clean.
        """
        args = self.diff_args()
        completed_process = args.run(check=False)
        return completed_process.stdout

    def diff_quiet_args(self, *args: str) -> Args:
        """Build arguments for ``git diff --quiet``.

        The ``--quiet`` flag suppresses all output and signals the presence of
        differences through the process exit code only.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git diff --quiet [args]``.
        """
        return self.diff_args("--quiet", *args)

    def diff_args(self, *args: str) -> Args:
        """Build base arguments for ``git diff``.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git diff [args]``.
        """
        return self.args("diff", *args)

    # -------------------------------------------------------------------------
    # Repository metadata
    # -------------------------------------------------------------------------

    @classmethod
    @cache
    def repo_owner_and_name(
        cls, *, check_repo_url: bool = True, url_encode: bool = False
    ) -> tuple[str, str]:
        """Return the cached repository owner and name.

        This is the primary public entry point for obtaining repository
        identity.  It delegates to ``_repo_owner_and_name`` on a fresh instance
        and caches the result at the class level so that repeated calls within
        the same process incur no subprocess overhead.

        Args:
            check_repo_url: When ``True``, raises an error if no remote origin
                is configured.  Set to ``False`` to fall back gracefully to the
                git user name and the current project name.
            url_encode: When ``True``, percent-encodes the returned strings,
                which is required when embedding them directly in URLs.

        Returns:
            A ``(owner, repository_name)`` tuple of strings.
        """
        return cls()._repo_owner_and_name(  # noqa: SLF001
            check_repo_url=check_repo_url, url_encode=url_encode
        )

    def _repo_owner_and_name(
        self,
        *,
        check_repo_url: bool = True,
        url_encode: bool = False,
    ) -> tuple[str, str]:
        """Parse the repository owner and name from the git remote URL.

        Supports both HTTPS (``https://github.com/owner/repo.git``) and SSH
        (``git@github.com:owner/repo.git``) remote formats by taking the last
        two path segments after stripping the ``.git`` suffix and splitting on
        ``/``.  The SSH colon separator in the owner segment is handled
        explicitly.

        When no remote is configured, falls back to the git ``user.name`` as
        the owner and the current project name from ``PackageManager`` as the
        repository name.

        Args:
            check_repo_url: When ``True``, raises an error if no remote origin
                is configured.
            url_encode: When ``True``, percent-encodes the returned strings.

        Returns:
            A ``(owner, repository_name)`` tuple of strings.
        """
        url = self.repo_remote(check=check_repo_url)
        if not url:
            # we default to git username and repo name from cwd
            logger.debug(
                "No git remote found, using git username and CWD for repo info"
            )
            owner = self.username()
            repo = PackageManager.I.project_name()
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

    def repo_remote(self, *, check: bool = True) -> str:
        """Return the remote origin URL configured for this repository.

        Reads ``remote.origin.url`` via ``git config --get`` and strips
        surrounding whitespace from the output.

        Args:
            check: When ``True``, raises ``subprocess.CalledProcessError`` if
                the command fails (e.g. no remote is configured).  When
                ``False``, returns an empty string on failure.

        Returns:
            The remote URL string in HTTPS or SSH format, or an empty string
            when ``check=False`` and no remote origin is configured.

        Raises:
            subprocess.CalledProcessError: When ``check=True`` and the git
                command exits with a non-zero status.
        """
        args = self.config_remote_origin_url_args()
        stdout = args.run_cached(check=check).stdout
        return stdout.strip()

    def username(self) -> str:
        """Return the git ``user.name`` from the active configuration.

        Used as the owner fallback inside ``_repo_owner_and_name`` when no
        remote origin is configured.

        Returns:
            The configured git user name string.

        Raises:
            subprocess.CalledProcessError: If ``user.name`` is not configured.
        """
        args = self.config_get_user_name_args()
        stdout = args.run_cached().stdout
        return stdout.strip()

    def email(self) -> str:
        """Return the git ``user.email`` from the active configuration.

        Returns:
            The configured git user email string.

        Raises:
            subprocess.CalledProcessError: If ``user.email`` is not configured.
        """
        args = self.config_get_user_email_args()
        stdout = args.run_cached().stdout
        return stdout.strip()
