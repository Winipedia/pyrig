"""Base class for Python config files that must reside within a valid package tree."""

from pathlib import Path

from pyrig.core.introspection.packages import make_package_dir
from pyrig.rig.configs.base.python import PythonConfigFile
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.programming_language import ProgrammingLanguage


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
