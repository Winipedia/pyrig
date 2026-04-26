"""Abstract base classes for tool wrappers.

Defines the ``Tool`` base class and ``ToolGroup`` constants that all tool
wrappers in pyrig and downstream packages must implement.
"""

from abc import abstractmethod
from collections import defaultdict
from types import ModuleType

from pyrig.core.strings import make_linked_badge_markdown
from pyrig.core.subprocesses import Args
from pyrig.rig import tools
from pyrig.rig.utils.dependency_subclass import RigDependencySubclass


class ToolGroup:
    """Named constants for tool badge groups.

    Used to categorize tool badges when rendering the project ``README.md``.
    """

    CI_CD = "ci/cd"
    CODE_QUALITY = "code-quality"
    DOCUMENTATION = "documentation"
    PROJECT_INFO = "project-info"
    SECURITY = "security"
    TOOLING = "tooling"
    TESTING = "testing"


class Tool(RigDependencySubclass):
    """Abstract base class for CLI tool wrappers.

    All tools in pyrig (linter, package manager, type checker, etc.) subclass
    ``Tool``. A subclass implements the three abstract methods to provide its
    identity (``name``), badge metadata (``group``, ``badge_urls``), and then
    adds ``*_args`` methods that return ``Args`` objects for each supported
    command.

    The ``Tool.I`` shortcut gives access to a cached singleton instance of the
    leaf subclass, which is the primary way tools are invoked from pyrig internals.

    Example:
        >>> class MyTool(Tool):
        ...     def name(self) -> str:
        ...         return "mytool"
        ...     def group(self) -> str:
        ...         return ToolGroup.TOOLING
        ...     def badge_urls(self) -> tuple[str, str]:
        ...         return ("https://img.shields.io/badge/my-badge", "https://mytool.io")
        ...     def build_args(self, *args: str) -> Args:
        ...         return self.args("build", *args)
        >>> MyTool.I.build_args("--verbose")
        Args(('mytool', 'build', '--verbose'))
    """

    def __str__(self) -> str:
        """Return the fully qualified class name with the tool name in parentheses.

        Returns:
            String in the form ``'package.ClassName (toolname)'``.
        """
        return f"{super().__str__()} ({self.name()})"

    @abstractmethod
    def name(self) -> str:
        """Return the CLI command name for this tool.

        This is the executable name used as the first element of every ``Args``
        object produced by this tool (e.g., ``"git"``, ``"uv"``, ``"pytest"``).

        Returns:
            The executable name as a string.
        """

    @abstractmethod
    def group(self) -> str:
        """Return the badge group this tool belongs to.

        Groups are used to categorize badges when rendering the project
        ``README.md``. Use one of the ``ToolGroup`` constants as the return value.

        Returns:
            A ``ToolGroup`` constant string (e.g., ``ToolGroup.TESTING``).
        """

    @abstractmethod
    def badge_urls(self) -> tuple[str, str]:
        """Return the badge image URL and link URL for this tool.

        These URLs are used to render a Markdown badge in the project
        ``README.md``. The badge image is typically hosted on shields.io or
        a similar service.

        Returns:
            A two-element tuple ``(badge_image_url, link_url)`` where
            ``badge_image_url`` is the URL of the badge image and ``link_url``
            is the page the user is taken to when clicking the badge.
        """

    @classmethod
    def definition_package(cls) -> ModuleType:
        """Return the ``pyrig.rig.tools`` package as the subclass discovery scope.

        Overrides ``RigDependencySubclass.definition_package`` to narrow discovery
        from the entire ``pyrig.rig`` namespace down to ``pyrig.rig.tools``,
        ensuring that only tool implementations are found when searching
        dependent packages.

        Returns:
            The ``pyrig.rig.tools`` module.
        """
        return tools

    @classmethod
    def grouped_badges(cls) -> defaultdict[str, list[str]]:
        """Return all tool badges grouped by their ``ToolGroup`` category.

        Collects every concrete ``Tool`` subclass, sorts them by ``sort_key``,
        and builds a mapping from group name to the list of Markdown badge
        strings for that group. Used by ``BadgesMdConfigFile`` to render the
        ``README.md``.

        Returns:
            A ``defaultdict`` mapping each group name to a list of Markdown
            badge strings for the tools in that group.
        """
        subclasses = cls.subclasses_sorted(cls.concrete_subclasses())
        groups: defaultdict[str, list[str]] = defaultdict(list)
        for tool in subclasses:
            t = tool()
            groups[t.group()].append(t.badge())
        return groups

    @classmethod
    def subclasses_dev_dependencies(cls) -> list[str]:
        """Return a sorted list of dev dependencies from all concrete tool subclasses.

        Iterates every concrete ``Tool`` subclass and collects its
        ``dev_dependencies`` to produce a unified, sorted list. This list is
        used when generating the ``[dependency-groups] dev`` section of
        ``pyproject.toml`` so that any tool added or removed from the rig is
        automatically reflected in the project's dependencies.

        Returns:
            Sorted list of dev dependency names across all tools.
        """
        return sorted(
            dep
            for subclass in cls.concrete_subclasses()
            for dep in subclass().dev_dependencies()
        )

    @classmethod
    def sort_key(cls) -> str:
        """Return the tool name as a sort key for stable alphabetical ordering.

        Overrides ``DependencySubclass.sort_key`` to sort by the tool's
        executable name rather than the class name, giving predictable ordering
        independent of class naming conventions.

        Returns:
            The tool's executable name (same as ``name()``).
        """
        return cls().name()

    def badge(self) -> str:
        """Return the Markdown badge string for this tool.

        Combines the URLs from ``badge_urls`` into a Markdown inline image
        that links to the tool's home page. The class name is used as alt text.

        Returns:
            A Markdown string in the form ``[![ClassName](badge_url)](link_url)``.
        """
        badge, page = self.badge_urls()
        return make_linked_badge_markdown(
            badge_url=badge,
            link_url=page,
            alt_text=self.__class__.__name__,
        )

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return the dev dependency names required by this tool.

        Used by ``subclasses_dev_dependencies`` to collect all tool dependencies
        for ``pyproject.toml``. Override in a subclass to declare a different
        set of packages, for example when a tool ships under a package name that
        differs from its executable name.

        Returns:
            A tuple of package names. Defaults to a single-element tuple
            containing the tool's executable name.
        """
        return (self.name(),)

    def args(self, *args: str) -> Args:
        """Construct an ``Args`` object with the tool name prepended.

        The core building block used by every ``*_args`` method in a ``Tool``
        subclass. Prepending ``name()`` ensures every constructed command
        starts with the correct executable.

        Args:
            *args: Command arguments to follow the tool name.

        Returns:
            An ``Args`` object whose first element is the tool name.

        Example:
            >>> PackageManager.I.args("run", "pytest")
            Args(('uv', 'run', 'pytest'))
        """
        return Args((self.name(), *args))
