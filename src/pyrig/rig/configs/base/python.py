"""Base class for managing Python (`.py`) source file configuration."""

from types import ModuleType
from typing import Any

from pyrig.core.introspection.modules import (
    import_module_with_file_fallback,
    reimport_module,
)
from pyrig.core.introspection.packages import import_package_with_dir_fallback
from pyrig.core.root import root_path_as_module_name
from pyrig.rig.configs.base.string_ import StringConfigFile


class PythonConfigFile(StringConfigFile):
    """Abstract base class for Python (`.py`) source files.

    The extension is always `"py"`.

    Subclasses must implement:
        - `parent_path`: Directory that will contain the `.py` file.
        - `stem`: Filename without its extension.
        - `lines`: Python source lines required to be present in the file.

    Example:
        >>> from pathlib import Path
        >>> from pyrig.rig.configs.base.python import PythonConfigFile
        >>>
        >>> class MyPythonFile(PythonConfigFile):
        ...
        ...     def parent_path(self) -> Path:
        ...         return Path("src")
        ...
        ...     def stem(self) -> str:
        ...         return "my_module"
        ...
        ...     def lines(self) -> list[str]:
        ...         return ["from typing import Any", "import sys"]
    """

    def extension(self) -> str:
        """Return `"py"`, the fixed extension for Python source files."""
        return "py"

    def _dump(self, configs: list[Any]) -> None:
        """Reimport the module after the config file is written."""
        super()._dump(configs)
        reimport_module(self.module(), is_package=self.is_init_file())

    def module(self) -> ModuleType:
        """Return the module for this config file.

        Returns:
            The package module at the parent path for `__init__` files, or the
            module at the file path otherwise.
        """
        if self.is_init_file():
            import_func = import_package_with_dir_fallback
            path = self.parent_path()
        else:
            import_func = import_module_with_file_fallback
            path = self.path()
        return import_func(path, root_path_as_module_name(path))

    def is_init_file(self) -> bool:
        """Check if this config file is an `__init__.py`."""
        return self.stem() == "__init__"
