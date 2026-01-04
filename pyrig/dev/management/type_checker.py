"""Ty type checker wrapper.

Provides type-safe wrapper for ty commands: check.
Ty is Astral's extremely fast Python type checker.

Example:
    >>> from pyrig.dev.management.type_checker import TypeChecker
    >>> TypeChecker.L.get_check_args().run()
"""

from pyrig.dev.management.base.base import Tool
from pyrig.src.processes import Args


class TypeChecker(Tool):
    """Ty type checker wrapper.

    Constructs ty command arguments for type checking operations.

    Operations:
        - Type checking: Verify type annotations and correctness

    Example:
        >>> TypeChecker.L.get_check_args().run()
        >>> TypeChecker.L.get_check_args("src/").run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'ty'
        """
        return "ty"

    @classmethod
    def get_check_args(cls, *args: str) -> Args:
        """Construct ty check arguments.

        Args:
            *args: Check command arguments.

        Returns:
            Args for 'ty check'.
        """
        return cls.get_args("check", *args)
