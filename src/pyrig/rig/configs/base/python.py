r"""Abstract base class for Python source file configuration.

Provides ``PythonConfigFile`` as the base for all generated ``.py`` files,
setting a fixed ``"py"`` extension on top of the string-based config system.
"""

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
    """Abstract base class for Python (``.py``) source files.

    Fixes the file extension to ``"py"`` and inherits all content validation,
    file I/O, and update logic from ``StringConfigFile``.

    Subclasses must implement:
        - ``parent_path``: The directory that will contain the ``.py`` file.
        - ``stem``: The filename without its extension.
        - ``lines``: The Python source lines required to be present in the file.

    Example:
        Define a concrete Python config file::

            from pathlib import Path
            from pyrig.rig.configs.base.python import PythonConfigFile

            class MyPythonFile(PythonConfigFile):

                def parent_path(self) -> Path:
                    return Path("src")

                def stem(self) -> str:
                    return "my_module"

                def lines(self) -> list[str]:
                    return ["from typing import Any", "import sys"]
    """

    def extension(self) -> str:
        """Return the file extension for Python source files.

        Returns:
            ``"py"``
        """
        return "py"

    def _dump(self, configs: list[Any]) -> None:
        """Reimports the module after a dump to reflect possible changes."""
        super()._dump(configs)
        reimport_module(self.module(), is_package=self.is_init_file())

    def module(self) -> ModuleType:
        """Import and return the module represented by this config file.

        Uses a file fallback import strategy for regular modules, or a package
        directory fallback strategy for ``__init__`` files, to ensure the module
        can be imported.

        Returns:
            Imported module corresponding to the config file's path.
        """
        if self.is_init_file():
            import_func = import_package_with_dir_fallback
            path = self.parent_path()
        else:
            import_func = import_module_with_file_fallback
            path = self.path()
        return import_func(path, root_path_as_module_name(path))

    def is_init_file(self) -> bool:
        """Check if this config file is an ``__init__.py``.

        Returns:
            True if the file stem is ``"__init__"``, False otherwise.
        """
        return self.stem() == "__init__"
