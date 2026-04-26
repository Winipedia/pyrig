"""Config base class for generating ``__init__.py`` files with copied module docstrings.

Example:
    >>> from types import ModuleType
    >>> from pyrig.rig.configs.base.init import InitConfigFile
    >>> import pyrig.rig.configs
    >>>
    >>> class ConfigsPackageInit(InitConfigFile):
    ...
    ...     def copy_module(self) -> ModuleType:
    ...         return pyrig.rig.configs
    >>>
    >>> ConfigsPackageInit()  # Creates <project>/rig/configs/__init__.py
"""

from pathlib import Path

import pyrig
from pyrig.core.introspection.modules import leaf_module_name
from pyrig.rig.configs.base.copy_module_docstring import (
    CopyModuleDocstringConfigFile,
)
from pyrig.rig.tools.package_manager import PackageManager


class InitConfigFile(CopyModuleDocstringConfigFile):
    """Base class for generating ``__init__.py`` files with copied module docstrings.

    The filename is always ``__init__``. The parent directory is derived from the
    source module's dotted name, with path transformation applied so that the file
    lands inside the target project's package tree rather than pyrig's own tree.

    Subclasses must implement:
        - ``copy_module``: Return the source module whose docstring will be written.
    """

    def parent_path(self) -> Path:
        """Return the directory that will contain the generated ``__init__.py``.

        ``CopyModuleConfigFile.parent_path`` resolves a module's dotted name to a
        filesystem path and returns its *parent directory* — the directory that would
        hold a regular ``.py`` file of that name.  For an ``__init__.py`` the file
        lives one level deeper: inside the package directory itself.  This override
        corrects for that by appending the package directory name to the path returned
        by the parent implementation.

        The directory name is determined as follows:

        - If ``copy_module`` is the ``pyrig`` root package, the target project's
          package name is used instead (obtained from
          ``PackageManager.I.package_name()``).  This is necessary because ``pyrig``
          has no meaningful leaf name to use for the generated project.
        - For every other module the last component of its dotted name is used
          (e.g. ``"configs"`` for ``pyrig.rig.configs``).

        Returns:
            Absolute-or-relative path to the directory where ``__init__.py`` will be
            written (e.g. ``src/myproject/rig/configs/`` for a configs package).
        """
        path = super().parent_path()
        # this path will be parent of the init file
        copy_module = self.copy_module()
        dir_name = (
            leaf_module_name(copy_module)
            if copy_module is not pyrig
            else PackageManager.I.package_name()
        )
        return path / dir_name

    def stem(self) -> str:
        """Return ``"__init__"`` as the filename stem for all ``__init__.py`` files.

        Returns:
            The string ``"__init__"``.
        """
        return "__init__"
