"""Base class for managing Python (`.py`) source file configuration."""

from pathlib import Path
from types import ModuleType
from typing import Any

from pyrig.core.introspection.modules import (
    import_module_with_file_fallback,
    reimport_module,
)
from pyrig.core.introspection.paths import path_as_module_name
from pyrig.rig.configs.base.string_ import StringConfigFile


class PythonConfigFile(StringConfigFile):
    r"""Abstract base class for Python (`.py`) source files.

    The extension is always `"py"`.

    Subclasses must implement:
        - `parent_path`: Directory that will contain the `.py` file.
        - `stem`: Filename without its extension.
        - `content`: Python source required to be present in the file.

    Example:
        >>> from pathlib import Path
        >>> from pyrig.rig.configs.base.python import PythonConfigFile
        >>>
        >>> class MyPythonFile(PythonConfigFile):
        ...     def parent_path(self) -> Path:
        ...         return Path("src")
        ...
        ...     def stem(self) -> str:
        ...         return "my_module"
        ...
        ...     def content(self) -> str:
        ...         return "from typing import Any\nimport sys"
    """

    def _dump(self, configs: list[Any]) -> None:
        """Reimport the module after the config file is written."""
        super()._dump(configs)
        reimport_module(self.module())

    def extension(self) -> str:
        """Return `"py"`, the fixed extension for Python source files."""
        return "py"

    def module(self) -> ModuleType:
        """Return the imported module this config file manages.

        Returns:
            Module imported from this config file's import path.
        """
        path = self.import_path()
        return import_module_with_file_fallback(
            path,
            path_as_module_name(path.relative_to(self.source_root())),
        )

    def import_path(self) -> Path:
        """Return the path from which this config file's module is imported.

        Returns:
            The config file's path.
        """
        return self.path()

    def source_root(self) -> Path:
        """Return the directory this file's path is relative to for its module name.

        Defaults to the project root; subclasses whose files live under a
        dedicated source directory override it.
        """
        return Path()
