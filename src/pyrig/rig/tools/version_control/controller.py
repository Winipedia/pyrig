"""Type-safe construction of version control CLI commands and identity resolution."""

from functools import cache

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


class VersionController(Tool):
    """Git tool wrapper exposing typed command builders and identity resolution.

    Every `*_args` method returns an `Args` command prefixed with `git`, ready
    to run or to render as a shell string. Other methods resolve the
    repository owner and the local git user's configured identity.
    """

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return an empty tuple; git is a system dependency, not a pip package."""
        return ()

    def group(self) -> str:
        """Return `Group.TOOLING` as the badge category."""
        return Group.TOOLING

    def image_url(self) -> str:
        """Return the Shields.io badge image URL for Git."""
        return f"https://img.shields.io/badge/Git-F05032?logo={self.name()}&logoColor=white"

    def link_url(self) -> str:
        """Return the URL of the Git homepage."""
        return "https://git-scm.com"

    def name(self) -> str:
        """Return `'git'` as the executable name."""
        return "git"

    @classmethod
    @cache
    def repo_owner(cls) -> str:
        """Return the repository owner.

        Returns:
            The repository owner.
        """
        return cls().resolve_repo_owner()

    def resolve_repo_owner(self) -> str:
        """Return the repository owner, falling back to the local git username.

        Returns:
            The owner parsed from the remote origin URL, or the local
            `user.name` (normalized) if no remote origin is configured.
        """
        return self.remote_repo_owner() or self.normalized_username()

    def default_branch(self) -> str:
        """Return `'main'` as this project's default branch name."""
        return "main"

    def end_of_line(self) -> str:
        """Return `'lf'`, the project's line-ending convention."""
        return "lf"

    def init_args(self, *args: str) -> Args:
        """Build arguments for `git init`.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `git init [args]`.
        """
        return self.args("init", *args)

    def add_all_args(self, *args: str) -> Args:
        """Build arguments equivalent to running `git add .`.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `git add . [args]`.
        """
        return self.add_args(".", *args)

    def add_args(self, *args: str) -> Args:
        """Build base arguments for `git add`.

        Args:
            *args: Files or paths to stage.

        Returns:
            Args for `git add [args]`.
        """
        return self.args("add", *args)

    def commit_with_msg_args(self, *args: str, msg: str) -> Args:
        """Build arguments for `git commit --message=<msg>`.

        Args:
            *args: Additional arguments appended to the command.
            msg: The commit message.

        Returns:
            Args for `git commit --message=<msg> [args]`.
        """
        return self.commit_args(f"--message={msg}", *args)

    def commit_args(self, *args: str) -> Args:
        """Build base arguments for `git commit`.

        Args:
            *args: Commit options or message flags (e.g. `--message`, `--amend`).

        Returns:
            Args for `git commit [args]`.
        """
        return self.args("commit", *args)

    def config_get_user_email_args(self, *args: str) -> Args:
        """Build arguments to read the configured `user.email` value.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `git config --get user.email [args]`.
        """
        return self.config_get_args("user.email", *args)

    def config_get_username_args(self, *args: str) -> Args:
        """Build arguments to read the configured `user.name` value.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `git config --get user.name [args]`.
        """
        return self.config_get_args("user.name", *args)

    def config_remote_origin_url_args(self, *args: str) -> Args:
        """Build arguments to read the `remote.origin.url` value.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `git config --get remote.origin.url [args]`.
        """
        return self.config_get_args("remote.origin.url", *args)

    def config_get_args(self, *args: str) -> Args:
        """Build base arguments for `git config --get`.

        The `--get` flag instructs git to print the value for the given key
        and exit with a non-zero code when the key is absent.

        Args:
            *args: The configuration key to query, and any additional
                arguments appended to the command.

        Returns:
            Args for `git config --get [args]`.
        """
        return self.config_args("--get", *args)

    def config_args(self, *args: str) -> Args:
        """Build base arguments for `git config`.

        Args:
            *args: Config subcommands, scope flags, and key/value pairs.

        Returns:
            Args for `git config [args]`.
        """
        return self.args("config", *args)

    def remote_repo_owner(self) -> str:
        """Return the repository owner parsed from the remote origin URL.

        Supports HTTPS (`https://github.com/owner/repo.git`) and SSH
        (`git@github.com:owner/repo.git` or `ssh://git@github.com/owner/repo.git`)
        remote formats.

        Returns:
            The repository owner, or an empty string if no remote origin
            is configured.
        """
        url = self.remote_url()
        # possible formats:
        # ssh://git@github.com/owner/repo.git
        # git@github.com:owner/repo.git
        # https://github.com/owner/repo.git
        url = url.split("github.com", 1)[-1]  # split off the domain, keep the path
        url = url.removeprefix("/").removeprefix(":")
        # the url left must have the format: owner/repo.git
        return url.split("/")[0]

    def remote_url(self) -> str:
        """Return the remote origin URL configured for this repository.

        Returns:
            The configured `remote.origin.url` value, or an empty string if
            no remote origin is configured.
        """
        return (
            self.config_remote_origin_url_args().run_cached(check=False).stdout.strip()
        )

    def normalized_username(self) -> str:
        """Return the git `user.name` with spaces removed.

        Returns:
            The configured git user name with spaces removed.

        Raises:
            subprocess.CalledProcessError: If `user.name` is not configured.
        """
        return self.username().replace(" ", "")

    def username(self) -> str:
        """Return the git `user.name` from the active configuration.

        Returns:
            The configured git user name.

        Raises:
            subprocess.CalledProcessError: If `user.name` is not configured.
        """
        return self.config_get_username_args().run_cached().stdout.strip()

    def email(self) -> str:
        """Return the git `user.email` from the active configuration.

        Returns:
            The configured git user email.

        Raises:
            subprocess.CalledProcessError: If `user.email` is not configured.
        """
        return self.config_get_user_email_args().run_cached().stdout.strip()

    def has_commits(self) -> bool:
        """Return whether the repository has at least one commit.

        Returns:
            `True` if the repository has at least one commit; `False`
            otherwise.
        """
        return (
            self.rev_parse_verify_args("HEAD").run_cached(check=False).returncode == 0
        )

    def rev_parse_verify_args(self, *args: str) -> Args:
        """Build arguments for `git rev-parse --verify`.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `git rev-parse --verify [args]`.
        """
        return self.rev_parse_args("--verify", *args)

    def rev_parse_args(self, *args: str) -> Args:
        """Build arguments for `git rev-parse`.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `git rev-parse [args]`.
        """
        return self.args("rev-parse", *args)
