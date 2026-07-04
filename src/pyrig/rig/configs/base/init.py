"""Base configuration for `__init__.py` generation from a module's docstring."""

from pathlib import Path

import pyrig
from pyrig.core.introspection.modules import leaf_module_name
from pyrig.rig.configs.base.copy_module_docstring import (
    CopyModuleDocstringConfigFile,
)
from pyrig.rig.tools.package_manager import PackageManager


class InitConfigFile(CopyModuleDocstringConfigFile):
    """Base class for `__init__.py` config files containing a copied module docstring.

    The generated file is always named `__init__.py` and is placed inside the
    package directory corresponding to the source module in the target project's tree.

    Subclasses must implement:
        - `copy_module`: Return the source module whose docstring will be written.
    """

    def parent_path(self) -> Path:
        """Return the directory that will contain the generated `__init__.py`.

        The returned path is the package directory for `copy_module` within the
        target project's source tree. When `copy_module` is the `pyrig` root
        package, the directory is named after the target project's package
        rather than `pyrig`.

        Returns:
            Path to the package directory where `__init__.py` will be written
            (e.g., `src/myproject/rig/configs` for a configs package).
        """
        path = super().parent_path()
        copy_module = self.copy_module()
        dir_name = (
            leaf_module_name(copy_module)
            if copy_module is not pyrig
            else PackageManager.I.package_name()
        )
        return path / dir_name

    def stem(self) -> str:
        """Return `"__init__"` as the filename stem."""
        return "__init__"
