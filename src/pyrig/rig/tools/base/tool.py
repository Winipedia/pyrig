"""Abstract base classes for tool wrappers.

Defines the ``Tool`` base class and ``Group`` constants that all tool
wrappers in pyrig and downstream packages must implement.
"""

from abc import abstractmethod
from types import ModuleType

from pyrig_runtime.core.dependencies.subclass import DependencySubclass

from pyrig.core.strings import make_linked_badge_markdown
from pyrig.core.subprocesses import Args
from pyrig.rig import tools


class Group:
    """Named constants for tool badge groups.

    Used to categorize tool badges when rendering the project ``README.md``.
    """

    CI_CD = "ci/cd"
    CODE_QUALITY = "code-quality"
    PROJECT_INFO = "project-info"
    TOOLING = "tooling"
    TESTING = "testing"


class Tool(DependencySubclass):
    """Abstract base class for CLI tool wrappers.

    All tools in pyrig (linter, package manager, type checker, etc.) subclass
    ``Tool``. A subclass implements the four abstract methods to provide its
    identity (``name``), badge metadata (``group``, ``image_url``,
    ``link_url``), and then adds ``*_args`` methods that return ``Args`` objects
    for each supported command.

    The ``Tool.I`` shortcut gives access to a cached singleton instance of the
    leaf subclass, which is the primary way tools are invoked from pyrig internals.

    Example:
        >>> class MyTool(Tool):
        ...     def name(self) -> str:
        ...         return "mytool"
        ...     def group(self) -> str:
        ...         return Group.TOOLING
        ...     def image_url(self) -> str:
        ...         return "https://img.shields.io/badge/my-badge"
        ...     def link_url(self) -> str:
        ...         return "https://mytool.io"
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
        ``README.md``. Use one of the ``Group`` constants as the return value.

        Returns:
            A ``Group`` constant string (e.g., ``Group.TESTING``).
        """

    @abstractmethod
    def image_url(self) -> str:
        """Return the URL of the badge image for this tool.

        This is used to render a markdown badges.

        Returns:
            The URL of the badge image as a string.
        """

    @abstractmethod
    def link_url(self) -> str:
        """Return the URL that the badge should link to for this tool.

        This is used to render a markdown badges.

        Returns:
            The URL that the badge should link to as a string.
        """

    def version_control_ignore_paths(self) -> tuple[str, ...]:
        """Return a tuple of file paths to ignore for version control.

        Used by pyrig's project initialization logic to automatically add
        tool-specific files (e.g., cache directories) to the
        project's ``.gitignore``. Override in a subclass to specify the paths
        relevant to that tool.

        Returns:
            A tuple of file paths (relative to the project root) that should be
            added to version control ignore files. Defaults to an empty tuple.
        """
        return ()

    @classmethod
    def dependency_package(cls) -> ModuleType:
        """Return the ``pyrig.rig.tools`` package as the subclass discovery scope.

        Implements the abstract ``DependencySubclass.dependency_package`` with
        the ``pyrig.rig.tools`` sub-package, so that only tool implementations
        are found when searching dependent packages.

        Returns:
            The ``pyrig.rig.tools`` module.
        """
        return tools

    @classmethod
    def grouped_badges(cls) -> dict[str, list[str]]:
        """Return all tool badges grouped by their ``Group`` category.

        Collects every concrete ``Tool`` subclass, sorts them by ``sort_key``,
        and builds a mapping from group name to the list of Markdown badge
        strings for that group. Used by ``BadgesConfigFile`` to render the
        ``README.md``.

        Returns:
            A ``dict`` mapping each group name to a list of Markdown badge
            strings for the tools in that group.
        """
        subclasses = cls.subclasses_sorted(cls.concrete_subclasses())
        groups: dict[str, list[str]] = {g: [] for g in cls.groups()}
        for subclass in subclasses:
            tool = subclass()
            groups[tool.group()].append(tool.badge())
        return groups

    @classmethod
    def groups(cls) -> tuple[str, ...]:
        """Get the ordering of the tool groups."""
        return (
            Group.CI_CD,
            Group.TESTING,
            Group.CODE_QUALITY,
            Group.TOOLING,
            Group.PROJECT_INFO,
        )

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
    def subclasses_version_control_ignore_paths(cls) -> list[str]:
        """Return a sorted list of version control ignore paths for all tools.

        Iterates every concrete ``Tool`` subclass and collects its
        ``version_control_ignore_paths`` to produce a unified, sorted list.
        """
        return sorted(
            path
            for subclass in cls.concrete_subclasses()
            for path in subclass().version_control_ignore_paths()
        )

    def badge(self) -> str:
        """Return the Markdown badge string for this tool.

        Combines ``image_url`` and ``link_url`` into a Markdown inline image
        that links to the tool's home page. The class name is used as alt text.

        Returns:
            A Markdown string in the form ``[![ClassName](image_url)](link_url)``.
        """
        return make_linked_badge_markdown(
            image_url=self.image_url(),
            link_url=self.link_url(),
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
