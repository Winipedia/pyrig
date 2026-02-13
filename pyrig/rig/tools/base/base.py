"""Base classes for type-safe command-line argument construction.

Provides `Tool` (base for tool wrappers).

Design pattern:
    1. Each tool (uv, git, pytest) is a `Tool` subclass
    2. Tool methods return `Args` objects (command argument tuples)
    3. `Args` objects execute directly or convert to strings
    4. All command construction centralized and testable

Benefits:
    - Type safety: Arguments validated at construction
    - Composability: Args combined and extended
    - Testability: Command construction tested without execution
    - Discoverability: IDE autocomplete shows available commands

Example:
    >>> from pyrig.rig.tools.package_manager import PackageManager
    >>> args = PackageManager.L.install_dependencies_args()
    >>> print(args)
    uv sync
    >>> args.run()
    CompletedProcess(...)
"""

import logging
from abc import abstractmethod
from collections import defaultdict
from types import ModuleType
from typing import Self

from pyrig.rig import tools
from pyrig.src.processes import Args
from pyrig.src.string_ import make_linked_badge_markdown
from pyrig.src.subclass import DependencySubclass

logger = logging.getLogger(__name__)


class ToolGroup:
    """Constants for badge groups."""

    CI_CD = "ci/cd"
    CODE_QUALITY = "code-quality"
    DOCUMENTATION = "documentation"
    PROJECT_INFO = "project-info"
    SECURITY = "security"
    TOOLING = "tooling"
    TESTING = "testing"


class Tool(DependencySubclass):
    """Abstract base for tool command argument construction.

    Provides consistent interface for constructing command-line arguments.
    Subclasses implement `name` and provide `*_args` methods.

    Pattern:
        - Each tool method returns `Args` object
        - Method names indicate command being constructed
        - Arguments validated at construction
        - Commands testable without execution

    Example:
        >>> class MyTool(Tool):
        ...     @classmethod
        ...     def name(cls) -> str:
        ...         return "mytool"
        ...     @classmethod
        ...     def build_args(cls, *args: str) -> Args:
        ...         return cls.args("build", *args)
        >>> MyTool.build_args("--verbose")
        Args(('mytool', 'build', '--verbose'))
    """

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Get tool command name.

        Returns:
            Tool command name (e.g., "git", "uv", "pytest").
        """

    @classmethod
    @abstractmethod
    def group(cls) -> str:
        """Returns the group the tools belongs to.

        Used e.g. for grouping badges in the Readme.md file.

        E.g. testing, tool, code-quality etc...
        """

    @classmethod
    @abstractmethod
    def badge_urls(cls) -> tuple[str, str]:
        """Returns the url for a badge, like found in a Readme.md file.

        The first url is the picture, the badge, and the second the link
        where you are led when clicking on the badge.

        Returns:
            a tuple of two str that are urls.
        """

    @classmethod
    def definition_package(cls) -> ModuleType:
        """Get the package where the tool subclasses are supposed to be defined."""
        return tools

    @classmethod
    def sorting_key(cls, subclass: type[Self]) -> str:
        """Return a sort key for the given tool subclass.

        The returned value is used to order discovered tool subclasses. The
        base implementation returns the tool's name which provides a stable
        alphabetical ordering. Subclasses may override to sort by priority or
        other criteria.

        Args:
            subclass (type[Self]): The subclass to compute a key for.

        Returns:
            str: A value suitable for use as a sort key.
        """
        return subclass.name()

    @classmethod
    def badge(cls) -> str:
        """Returns the badge string for a markdown file."""
        badge, page = cls.badge_urls()
        return make_linked_badge_markdown(
            badge_url=badge,
            link_url=page,
            alt_text=cls.name(),
        )

    @classmethod
    def dev_dependencies(cls) -> list[str]:
        """Get tool dependencies.

        Returns:
            List of tool dependencies. Defaults to the name of the tool.
        """
        return [cls.name()]

    @classmethod
    def args(cls, *args: str) -> Args:
        """Construct command arguments with tool name prepended.

        Args:
            *args: Command arguments.

        Returns:
            Args object with tool name and arguments.

        Note:
            Subclasses provide higher-level methods calling this internally.
        """
        return Args((cls.name(), *args))

    @classmethod
    def grouped_badges(cls) -> dict[str, list[str]]:
        """Get a dict with all badges of tools grouped by their group."""
        subclasses = cls.subclasses()
        groups: defaultdict[str, list[str]] = defaultdict(list)
        for tool in subclasses:
            groups[tool.group()].append(tool.badge())
        return groups

    @classmethod
    def subclasses_dev_dependencies(cls) -> list[str]:
        """Get all dev dependencies for all tools.

        This gets all subclasses of Tools and calls dev_dependencies() on them.
        This way all dependencies for each tool are retrieved.
        If a user adjusts a tool, this way he can make sure that the dev dependencies
        are added to the pyproject.toml and he can remove the ones of the tool he
        replaced.

        Returns:
            List of all tool dependencies.
        """
        subclasses = cls.subclasses()
        all_dev_deps: list[str] = []
        for subclass in subclasses:
            all_dev_deps.extend(subclass.dev_dependencies())
        return sorted(all_dev_deps)
