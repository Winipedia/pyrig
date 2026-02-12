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
    >>> args = PackageManager.L.get_install_dependencies_args()
    >>> print(args)
    uv sync
    >>> args.run()
    CompletedProcess(...)
"""

import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Self

import pyrig
from pyrig.rig import tools
from pyrig.src.modules.class_ import classproperty
from pyrig.src.modules.package import (
    discover_leaf_subclass_across_dependents,
    discover_subclasses_across_dependents,
)
from pyrig.src.processes import Args
from pyrig.src.string_ import make_linked_badge_markdown

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


class Tool(ABC):
    """Abstract base for tool command argument construction.

    Provides consistent interface for constructing command-line arguments.
    Subclasses implement `name` and provide `get_*_args` methods.

    Pattern:
        - Each tool method returns `Args` object
        - Method names indicate command being constructed
        - Arguments validated at construction
        - Commands testable without execution

    Example:
        >>> class MyTool(Tool):
        ...     @classmethod
        ...     def get_name(cls) -> str:
        ...         return "mytool"
        ...     @classmethod
        ...     def get_build_args(cls, *args: str) -> Args:
        ...         return cls.get_args("build", *args)
        >>> MyTool.get_build_args("--verbose")
        Args(('mytool', 'build', '--verbose'))
    """

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Get tool command name.

        Returns:
            Tool command name (e.g., "git", "uv", "pytest").
        """

    @classmethod
    @abstractmethod
    def get_group(cls) -> str:
        """Returns the group the tools belongs to.

        Used e.g. for grouping badges in the Readme.md file.

        E.g. testing, tool, code-quality etc...
        """

    @classmethod
    @abstractmethod
    def get_badge_urls(cls) -> tuple[str, str]:
        """Returns the url for a badge, like found in a Readme.md file.

        The first url is the picture, the badge, and the second the link
        where you are led when clicking on the badge.

        Returns:
            a tuple of two str that are urls.
        """

    @classmethod
    def get_badge(cls) -> str:
        """Returns the badge string for a markdown file."""
        badge, page = cls.get_badge_urls()
        return make_linked_badge_markdown(
            badge_url=badge,
            link_url=page,
            alt_text=cls.get_name(),
        )

    @classmethod
    def get_dev_dependencies(cls) -> list[str]:
        """Get tool dependencies.

        Returns:
            List of tool dependencies. Defaults to the name of the tool.
        """
        return [cls.get_name()]

    @classmethod
    def get_args(cls, *args: str) -> Args:
        """Construct command arguments with tool name prepended.

        Args:
            *args: Command arguments.

        Returns:
            Args object with tool name and arguments.

        Note:
            Subclasses provide higher-level methods calling this internally.
        """
        return Args((cls.get_name(), *args))

    @classproperty
    def L(cls) -> type[Self]:  # noqa: N802, N805
        """Get the final leaf subclass (deepest in the inheritance tree).

        Returns:
            Final leaf subclass type. Can be abstract.
        """
        return discover_leaf_subclass_across_dependents(
            cls=cls,
            dep=pyrig,
            load_pkg_before=tools,
        )

    @classmethod
    def get_all_subclasses(cls) -> list[type[Self]]:
        """Get all the tools subclasses.

        Finds all non abstract subclasses that are a final leave
        across dependecies of pyrig.

        Returns:
            _list of subclasses of the Tool class cls
        """
        return sorted(
            discover_subclasses_across_dependents(
                cls,
                pyrig,
                tools,
                discard_parents=True,
                exclude_abstract=True,
            ),
            key=lambda t: t.get_name(),
        )

    @classmethod
    def get_grouped_badges(cls) -> dict[str, list[str]]:
        """Get a dict with all badges of tools grouped by their group."""
        subclasses = cls.get_all_subclasses()
        groups = defaultdict(list)
        for tool in subclasses:
            groups[tool.get_group()].append(tool.get_badge())
        return groups

    @classmethod
    def get_all_tool_dev_deps(cls) -> list[str]:
        """Get all dev dependencies for all tools.

        This gets all subclasses of Tools and calls get_dev_dependencies() on them.
        This way all dependencies for each tool are retrieved.
        If a user adjusts a tool, this way he can make sure that the dev dependencies
        are added to the pyproject.toml and he can remove the ones of the tool he
        replaced.

        Returns:
            List of all tool dependencies.
        """
        subclasses = cls.get_all_subclasses()
        all_dev_deps: list[str] = []
        for subclass in subclasses:
            all_dev_deps.extend(subclass.get_dev_dependencies())
        return sorted(all_dev_deps)
