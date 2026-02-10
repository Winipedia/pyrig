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
from typing import Self

import pyrig
from pyrig.rig import tools
from pyrig.src.modules.class_ import classproperty
from pyrig.src.modules.package import (
    discover_leaf_subclass_across_dependents,
    discover_subclasses_across_dependents,
)
from pyrig.src.processes import Args

logger = logging.getLogger(__name__)


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
        ...     def name(cls) -> str:
        ...         return "mytool"
        ...     @classmethod
        ...     def get_build_args(cls, *args: str) -> Args:
        ...         return cls.get_args("build", *args)
        >>> MyTool.get_build_args("--verbose")
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
    def get_dev_dependencies(cls) -> list[str]:
        """Get tool dependencies.

        Returns:
            List of tool dependencies. Defaults to the name of the tool.
        """
        return [cls.name()]

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
        return Args((cls.name(), *args))

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
        subclasses = discover_subclasses_across_dependents(
            cls,
            pyrig,
            tools,
            discard_parents=True,
            exclude_abstract=True,
        )
        all_dev_deps: list[str] = []
        for subclass in subclasses:
            all_dev_deps.extend(subclass.get_dev_dependencies())
        return sorted(all_dev_deps)
