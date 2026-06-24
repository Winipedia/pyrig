"""Version controller wrapper.

Wraps VersionController commands and information.
"""

import logging
from functools import cache

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool

logger = logging.getLogger(__name__)


class VersionController(Tool):
    """Type-safe git command argument builder.

    Each ``*_args`` method constructs an ``Args`` object representing a specific git
    command.  ``Args`` objects can be executed directly via ``.run()`` or
    converted to a string for embedding in shell scripts and workflow files.
    All commands are automatically prefixed with ``git``.
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
            ``Group.TOOLING``
        """
        return Group.TOOLING

    def image_url(self) -> str:
        """Return the badge image URL for Git.

        Returns:
            The URL of the badge image as a string.
        """
        return "https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white"

    def link_url(self) -> str:
        """Return the link URL for Git.

        Returns:
            The URL of the Git project page as a string.
        """
        return "https://git-scm.com"

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

    def add_all_args(self, *args: str) -> Args:
        """Build arguments to stage all modified and untracked files.

        Equivalent to running ``git add .`` from the current working directory.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git add . [args]``.
        """
        return self.add_args(".", *args)

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

    def commit_with_msg_args(self, *args: str, msg: str) -> Args:
        """Build arguments for ``git commit -m <msg>``.

        Args:
            *args: Additional arguments appended to the command.
            msg: The commit message.

        Returns:
            Args for ``git commit -m <msg> [args]``.
        """
        return self.commit_args("-m", msg, *args)

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

    def push_origin_tag_args(self, *args: str, tag: str) -> Args:
        """Build arguments to push a specific tag to the ``origin`` remote.

        Used in release workflows to publish a version tag immediately after
        it has been created locally.

        Args:
            *args: Additional arguments appended to the command.
            tag: The tag ref to push (e.g. ``1.2.3``).

        Returns:
            Args for ``git push origin <tag> [args]``.
        """
        return self.push_origin_args(tag, *args)

    def push_origin_args(self, *args: str) -> Args:
        """Build arguments for ``git push origin``.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for ``git push origin [args]``.
        """
        return self.push_args("origin", *args)

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
            tag: The tag name to create (e.g. ``1.2.3``).

        Returns:
            Args for ``git tag <tag> [args]``.
        """
        return self.args("tag", tag, *args)

    # -------------------------------------------------------------------------
    # Configuration - write/set
    # -------------------------------------------------------------------------

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
    # Repository metadata
    # -------------------------------------------------------------------------

    @classmethod
    @cache
    def repo_owner(cls) -> str:
        """Return the cached repository owner.

        This is the primary public entry point for obtaining the repository
        owner.  It delegates to ``_repo_owner`` on a fresh instance
        and caches the result at the class level so that repeated calls within
        the same process incur no subprocess overhead.

        Returns:
            The repository owner as a string.
        """
        return cls()._repo_owner()  # noqa: SLF001

    def _repo_owner(self) -> str:
        """Parse the repository owner from the git remote URL.

        Supports both HTTPS (``https://github.com/owner/repo.git``) and SSH
        (``git@github.com:owner/repo.git``) remote formats by stripping known
        URL prefixes, then taking the first path segment as the owner.

        When no remote is configured and ````, falls back
        to the git ``user.name`` as the owner.

        If the fallback to git username is used, the spaces in the username are removed
        to ensure URL safety and a warning is logged. This is inspired by the fact that
        GitHub usernames cannot contain spaces in the URL, but git usernames can, so if
        the git username contains spaces, it is likely not intended to be used as-is
        for the repository owner in URLs.
        When extracting the owner from the remote URL, the username is guaranteed to be
        correct, so no correction is applied to it.


        Returns:
            The repository owner as a string.
        """
        url = self.remote_url(check=False)
        if not url:
            # we default to git username and repo name from cwd
            owner = self.user_name()
            logger.warning(
                "No remote url found, using git username: '%s' as repo owner",
                owner,
            )
            if " " in owner:
                logger.warning(
                    "Repository owner '%s' contains spaces.",
                    owner,
                )
                owner = owner.replace(" ", "")
                logger.warning(
                    "Spaces removed from the owner to ensure URL safety: '%s'",
                    owner,
                )
        else:
            owner = self.owner_from_remote_url()

        return owner

    def owner_from_remote_url(self) -> str:
        """Return the repository owner parsed from the remote URL.

        This method is a thin wrapper around ``remote_url()`` that extracts the
        owner segment from the URL.

        Returns:
            The repository owner as a string.

        Raises:
            subprocess.CalledProcessError: If no remote origin URL is configured.
        """
        url = self.remote_url(check=True)
        # possible formats:
        # ssh://git@github.com/owner/repo.git
        # git@github.com:owner/repo.git
        # https://github.com/owner/repo.git
        url = url.split("github.com", 1)[-1]  # split off the domain, keep the path
        url = url.removeprefix("/").removeprefix(":")
        # the url left must have the format: owner/repo.git
        owner = url.split("/")[0]
        logger.debug("Extracted owner from remote URL: %s", owner)
        return owner

    def remote_url(self, *, check: bool = True) -> str:
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
        return (
            self.config_remote_origin_url_args().run_cached(check=check).stdout.strip()
        )

    def user_name(self) -> str:
        """Return the git ``user.name`` from the active configuration.

        Used as the owner fallback inside ``_repo_owner`` when no
        remote origin is configured.

        Returns:
            The configured git user name string.

        Raises:
            subprocess.CalledProcessError: If ``user.name`` is not configured.
        """
        return self.config_get_user_name_args().run_cached().stdout.strip()

    def email(self) -> str:
        """Return the git ``user.email`` from the active configuration.

        Returns:
            The configured git user email string.

        Raises:
            subprocess.CalledProcessError: If ``user.email`` is not configured.
        """
        return self.config_get_user_email_args().run_cached().stdout.strip()
