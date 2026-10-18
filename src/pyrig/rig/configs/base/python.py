"""Base class for managing Python (`.py`) source file configuration."""

import ast
from pathlib import Path

from pyrig.core.introspection.packages import make_package_dir
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

    def extension(self) -> str:
        """Return `"py"`, the fixed extension for Python source files."""
        return "py"

    def source_root(self) -> Path:
        """Return the directory against which module paths for this file are resolved.

        Defaults to the project root; subclasses whose files live under a
        dedicated source directory override it.
        """
        return Path()

    def tree(self) -> ast.Module:
        """Return the AST of the Python source file represented by this config."""
        return ast.parse(self.read_content())


class PythonPackageConfigFile(PythonConfigFile):
    """Base class for Python source files that require a valid package tree.

    Before writing the file, ensures every directory from its parent up to
    and including the package root contains an `__init__.py`, making the
    generated file immediately importable.

    Use this class instead of `PythonConfigFile` whenever the generated file
    lives inside a package hierarchy that may not yet be fully initialized—for
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
