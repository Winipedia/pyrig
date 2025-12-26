"""Git version control wrapper for repository management.

This module provides a type-safe wrapper for Git version control commands.
The `VersionController` class constructs git command arguments for all common
version control operations including:
    - Repository initialization
    - Staging files (add)
    - Committing changes
    - Pushing to remotes
    - Tagging releases

Git is the primary version control system used by pyrig projects.

Example:
    >>> from pyrig.src.management.version_controller import VersionController
    >>> # Stage all files
    >>> add_args = VersionController.get_add_all_args()
    >>> add_args.run()
    >>>
    >>> # Commit with message
    >>> commit_args = VersionController.get_commit_no_verify_args("Update docs")
    >>> commit_args.run()
    >>>
    >>> # Push to remote
    >>> push_args = VersionController.get_push_args()
    >>> push_args.run()

See Also:
    pyrig.src.management.base.base.Tool: Base class for tool wrappers
    pyrig.src.git: Git repository information utilities
    pyrig.dev.cli.subcommands: CLI commands using VersionController
"""

from pyrig.src.management.base.base import Args, Tool


class VersionController(Tool):
    """Git version control tool wrapper.

    Provides methods for constructing git command arguments for all common
    version control operations. This centralizes git command construction
    and provides type-safe, discoverable methods for git operations.

    The class provides methods for:
        - **Repository setup**: init
        - **Staging**: add files, add all, add specific files
        - **Committing**: commit with various options
        - **Remote operations**: push, push tags
        - **Tagging**: create and push tags

    All methods return `Args` objects that can be executed via `.run()` or
    converted to strings for display.

    Example:
        >>> # Initialize repository
        >>> VersionController.get_init_args().run()
        >>>
        >>> # Stage and commit
        >>> VersionController.get_add_all_args().run()
        >>> VersionController.get_commit_no_verify_args("Initial commit").run()
        >>>
        >>> # Tag and push
        >>> VersionController.get_tag_args("v1.0.0").run()
        >>> VersionController.get_push_tags_args().run()

    See Also:
        pyrig.src.management.base.base.Tool: Base class
        pyrig.src.git: Git repository information utilities
    """

    @classmethod
    def name(cls) -> str:
        """Get the tool name.

        Returns:
            str: The string 'git'.
        """
        return "git"

    @classmethod
    def get_init_args(cls, *args: str) -> Args:
        """Construct git init command arguments.

        Args:
            *args: Additional arguments to append to the init command.

        Returns:
            Args: Command arguments for 'git init'.
        """
        return cls.get_args("init", *args)

    @classmethod
    def get_add_args(cls, *args: str) -> Args:
        """Construct git add command arguments.

        Args:
            *args: Files or paths to add to the staging area.

        Returns:
            Args: Command arguments for 'git add'.
        """
        return cls.get_args("add", *args)

    @classmethod
    def get_add_all_args(cls, *args: str) -> Args:
        """Construct git add command arguments for all files.

        Args:
            *args: Additional arguments to append to the add command.

        Returns:
            Args: Command arguments for 'git add .'.
        """
        return cls.get_add_args(".", *args)

    @classmethod
    def get_add_pyproject_toml_args(cls, *args: str) -> Args:
        """Construct git add command arguments for pyproject.toml.

        Args:
            *args: Additional arguments to append to the add command.

        Returns:
            Args: Command arguments for 'git add pyproject.toml'.
        """
        return cls.get_add_args("pyproject.toml", *args)

    @classmethod
    def get_add_pyproject_toml_and_uv_lock_args(cls, *args: str) -> Args:
        """Construct git add command arguments for pyproject.toml and uv.lock.

        Args:
            *args: Additional arguments to append to the add command.

        Returns:
            Args: Command arguments for 'git add pyproject.toml uv.lock'.
        """
        return cls.get_add_pyproject_toml_args("uv.lock", *args)

    @classmethod
    def get_commit_args(cls, *args: str) -> Args:
        """Construct git commit command arguments.

        Args:
            *args: Additional arguments to append to the commit command.

        Returns:
            Args: Command arguments for 'git commit'.
        """
        return cls.get_args("commit", *args)

    @classmethod
    def get_commit_no_verify_args(cls, msg: str, *args: str) -> Args:
        """Construct git commit command arguments with no verification.

        Args:
            msg: Commit message.
            *args: Additional arguments to append to the commit command.

        Returns:
            Args: Command arguments for 'git commit --no-verify -m <msg>'.
        """
        # wrap in quotes in case there are quotes in the message
        return cls.get_commit_args("--no-verify", "-m", msg, *args)

    @classmethod
    def get_push_args(cls, *args: str) -> Args:
        """Construct git push command arguments.

        Args:
            *args: Additional arguments to append to the push command.

        Returns:
            Args: Command arguments for 'git push'.
        """
        return cls.get_args("push", *args)

    @classmethod
    def get_config_args(cls, *args: str) -> Args:
        """Construct git config command arguments.

        Args:
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config'.
        """
        return cls.get_args("config", *args)

    @classmethod
    def get_config_global_args(cls, *args: str) -> Args:
        """Construct git config command arguments with --global flag.

        Args:
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config --global'.
        """
        return cls.get_config_args("--global", *args)

    @classmethod
    def get_config_local_args(cls, *args: str) -> Args:
        """Construct git config command arguments with --local flag.

        Args:
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config --local'.
        """
        return cls.get_config_args("--local", *args)

    @classmethod
    def get_config_local_user_email_args(cls, email: str, *args: str) -> Args:
        """Construct git config command arguments for user email.

        Args:
            email: Email address.
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config --local user.email <email>'.
        """
        return cls.get_config_local_args("user.email", email, *args)

    @classmethod
    def get_config_local_user_name_args(cls, name: str, *args: str) -> Args:
        """Construct git config command arguments for user name.

        Args:
            name: Name.
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config --local user.name <name>'.
        """
        return cls.get_config_local_args("user.name", name, *args)

    @classmethod
    def get_config_global_user_email_args(cls, email: str, *args: str) -> Args:
        """Construct git config command arguments for user email.

        Args:
            email: Email address.
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config user.email <email>'.
        """
        return cls.get_config_global_args("user.email", email, *args)

    @classmethod
    def get_config_global_user_name_args(cls, name: str, *args: str) -> Args:
        """Construct git config command arguments for user name.

        Args:
            name: Name.
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config user.name <name>'.
        """
        return cls.get_config_global_args("user.name", name, *args)
