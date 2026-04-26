"""Concrete ``py.typed`` marker file generator for the active project."""

from pathlib import Path

from pyrig.rig.configs.base.typed import TypedConfigFile
from pyrig.rig.tools.package_manager import PackageManager


class PyTypedConfigFile(TypedConfigFile):
    """PEP 561 ``py.typed`` marker file placed at the project's package root.

    The presence of a ``py.typed`` file at the package root signals to type checkers
    (mypy, pyright, ty, etc.) that the package ships inline type information and
    should be checked against its own annotations. The file must be empty; its mere
    existence carries all semantic meaning.
    """

    def stem(self) -> str:
        """Return ``"py"`` as the filename stem.

        Combined with the ``"typed"`` extension provided by the base class, this
        produces the filename ``py.typed``.
        """
        return "py"

    def parent_path(self) -> Path:
        """Return the root directory of the project's main package.

        Returns:
            Path to the package source directory (e.g. ``src/<package_name>``),
            as resolved by ``PackageManager``.
        """
        return PackageManager.I.package_root()
