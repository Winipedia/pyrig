"""Shared contract every external CLI tool wrapper must implement."""

from abc import abstractmethod
from types import ModuleType

from pyrig_runtime.core.dependencies.subclass import DependencySubclass
from pyrig_runtime.core.strings import kebab_to_snake_case

from pyrig.core.strings import make_linked_badge_markdown
from pyrig.core.subprocesses import Args
from pyrig.rig import tools


class Tool(DependencySubclass):
    """Abstract base for wrapping an external CLI tool's identity and commands.

    A subclass provides its identity and badge metadata through the abstract
    methods, then adds its own `*_args` methods that build `Args` for each
    command it supports.

    Example:
        >>> class MyTool(Tool):
        ...     def name(self) -> str:
        ...         return "mytool"
        ...
        ...     def group(self) -> str:
        ...         return Group.TOOLING
        ...
        ...     def image_url(self) -> str:
        ...         return "https://img.shields.io/badge/my-badge"
        ...
        ...     def link_url(self) -> str:
        ...         return "https://mytool.io"
        ...
        ...     def build_args(self, *args: str) -> Args:
        ...         return self.args("build", *args)
        >>> tuple(MyTool.I.build_args("--verbose"))
        ('mytool', 'build', '--verbose')
    """

    @abstractmethod
    def group(self) -> str:
        """Return the `Group` constant this tool's badge is categorized under."""

    @abstractmethod
    def image_url(self) -> str:
        """Return the URL of this tool's badge image."""

    @abstractmethod
    def link_url(self) -> str:
        """Return the URL this tool's badge should link to."""

    @abstractmethod
    def name(self) -> str:
        """Return the executable name for this tool's CLI command (e.g. `"git"`)."""

    @classmethod
    def discovery_module(cls) -> ModuleType:
        """Return the `pyrig.rig.tools` package as the tool discovery scope."""
        return tools

    @classmethod
    def grouped_badges(cls) -> dict[str, list[str]]:
        """Return every concrete tool's badge, grouped by its `Group` category.

        Returns:
            Mapping from each group name to the Markdown badge strings of the
            tools in that group. Groups are ordered by `groups()`; badges
            within a group are ordered by each tool's `sort_key()`.
        """
        subclasses = cls.subclasses_sorted(cls.concrete_subclasses())
        groups: dict[str, list[str]] = {g: [] for g in cls.groups()}
        for subclass in subclasses:
            tool = subclass()
            groups[tool.group()].append(tool.badge())
        return groups

    @classmethod
    def groups(cls) -> tuple[str, ...]:
        """Return the display order of the `Group` categories."""
        return (
            Group.PROJECT_STATUS,
            Group.CODE_QUALITY,
            Group.TOOLING,
            Group.PROJECT_INFO,
        )

    @classmethod
    def subclasses_dev_dependencies(cls) -> list[str]:
        """Return the dev dependency names of every concrete tool, sorted.

        Returns:
            Sorted list of dev dependency names across all tools. May contain
            duplicates if multiple tools share a dependency.
        """
        return sorted(
            {
                dep
                for subclass in cls.concrete_subclasses()
                for dep in subclass().dev_dependencies()
            },
        )

    @classmethod
    def subclasses_version_control_ignore_paths(cls) -> list[str]:
        """Return the version control ignore paths of every concrete tool, sorted.

        Returns:
            Sorted list of ignore paths across all tools. May contain
            duplicates if multiple tools share a path.
        """
        return sorted(
            path
            for subclass in cls.concrete_subclasses()
            for path in subclass().version_control_ignore_paths()
        )

    def args(self, *args: str) -> Args:
        """Build an `Args` command starting with this tool's executable name.

        Args:
            *args: Command arguments to follow the tool name.

        Returns:
            An `Args` object whose first element is the tool name.
        """
        return Args(self.name(), *args)

    def shield_name(self) -> str:
        """Return this tool's name escaped for a shields.io static badge segment.

        shields.io's static badge URL splits its path on `-`, so a literal
        hyphen in the name itself (e.g. `check-json`) must be doubled to
        `--` to survive as one segment instead of being misread as a field
        separator.

        Returns:
            `self.name()` with every `-` doubled.
        """
        return self.name().replace("-", "--")

    def badge(self) -> str:
        """Return the Markdown badge string for this tool.

        Returns:
            A Markdown string in the form `[![ClassName](image_url)](link_url)`.
        """
        return make_linked_badge_markdown(
            image_url=self.image_url(),
            link_url=self.link_url(),
            alt_text=self.__class__.__name__,
        )

    def config_name(self) -> str:
        """Return the normalized config name for this tool.

        Exists for purposes like the tool section of `pyproject.toml`
        where snake_case is more common than kebab-case.

        Returns:
            The tool's name as snake_case.
        """
        return kebab_to_snake_case(self.name())

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return the dev dependency names required by this tool.

        Override in a subclass to declare a different set of packages, for
        example when a tool ships under a package name that differs from its
        executable name.

        Returns:
            Package names. Defaults to a single-element tuple containing the
            tool's executable name.
        """
        return (self.name(),)

    def version_control_ignore_paths(self) -> tuple[str, ...]:
        """Return paths this tool writes that should be excluded from version control.

        Paths are relative to the project root. Override in a subclass to
        declare the tool's cache directories or other generated files.

        Returns:
            File paths to ignore. Empty by default.
        """
        return ()

    def __str__(self) -> str:
        """Add the tool name to the string representation.

        Returns:
            The class's string representation followed by the tool name in parentheses.
        """
        return f"{super().__str__()} ({self.name()})"


class Group:
    """Named constants for the categories tool badges are grouped under."""

    CODE_QUALITY = "code-quality"
    PROJECT_INFO = "project-info"
    PROJECT_STATUS = "project-status"
    TOOLING = "tooling"
