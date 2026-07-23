"""Base class for managing Python (`.py`) source file configuration."""

from pathlib import Path
from types import ModuleType
from typing import Any

from pyrig.core.introspection.modules import (
    import_module_with_file_fallback,
    reimport_module,
)
from pyrig.core.introspection.packages import make_package_dir
from pyrig.core.introspection.paths import path_as_module_name
from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.programming_language import ProgrammingLanguage


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


class PythonPackageConfigFile(PythonConfigFile):
    """Base class for Python source files that require a valid package tree.

    Before writing the file, ensures every directory from its parent up to
    and including the package root contains an `__init__.py`, making the
    generated file immediately importable.

    Use this class instead of `PythonConfigFile` whenever the generated file
    lives inside a package hierarchy that may not yet be fully initialised—for
    example, when scaffolding new sub-packages or mirror test modules.
    """

    def _dump(self, configs: list[str]) -> None:
        """Create any missing ancestor package directories, then write the file.

        Args:
            configs: Lines of Python source code to write to the target file.
        """
        make_package_dir(
            self.path().parent,
            root=self.package_root(),
            content=ProgrammingLanguage.I.standard_init_content(),
        )
        super()._dump(configs)

    def source_root(self) -> Path:
        """Return the source directory the package tree lives under."""
        return self.package_root().parent

    def package_root(self) -> Path:
        """Return the root directory of the package this config file belongs to."""
        return PackageManager.I.package_root()
