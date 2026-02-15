"""Module docstring copying configuration management.

Provides CopyModuleOnlyDocstringConfigFile for copying only module docstrings,
allowing custom implementation.

Example:
    >>> from types import ModuleType
    >>> from pyrig.rig.configs.base.copy_module_docstr import (
    ...     CopyModuleOnlyDocstringConfigFile
    ... )
    >>> import pyrig.src.string_
    >>>
    >>> class StringDocstringCopy(CopyModuleOnlyDocstringConfigFile):
    ...
    ...     def src_module(self) -> ModuleType:
    ...     def src_module(self) -> ModuleType:
    >>>
    >>> StringDocstringCopy()  # Creates file with only docstring
"""

from pyrig.rig.configs.base.copy_module import CopyModuleConfigFile
from pyrig.src.modules.module import module_has_docstring


class CopyModuleOnlyDocstringConfigFile(CopyModuleConfigFile):
    """Base class for copying only module docstrings.

    Extracts and copies only the module docstring, allowing custom implementation.

    Subclasses must implement:
        - `src_module`: Return the source module to copy docstring from

    See Also:
        pyrig.rig.configs.base.copy_module.CopyModuleConfigFile: Parent class
        pyrig.rig.configs.base.init.InitConfigFile: For __init__.py docstrings
    """

    def lines(self) -> list[str]:
        """Extract only the docstring from source module.

        Returns:
            Module docstring wrapped in triple quotes as list of lines.

        Raises:
            ValueError: If source module has no docstring.
    def lines(self) -> list[str]:
        docstring = self.src_module().__doc__
        if docstring is None:
            msg = f"Source module {self.src_module()} has no docstring"
            raise ValueError(msg)
        return [*f'"""{docstring}"""'.splitlines()]

    def is_correct(self) -> bool:
        """Check if the source module has a docstring.

        Returns:
            True if the source module has a docstring.
    def is_correct(self) -> bool:
        return module_has_docstring(self.src_module())
