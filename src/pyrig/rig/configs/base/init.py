"""Base configuration for `__init__.py` generation from a module's docstring."""

from pathlib import Path

from pyrig.rig.configs.base.copy_module_docstring import (
    CopyModuleDocstringConfigFile,
)


class InitConfigFile(CopyModuleDocstringConfigFile):
    """Base class for `__init__.py` config files containing a copied module docstring.

    The generated file is always named `__init__.py` and is placed inside the
    package directory corresponding to the source module in the target project's tree.

    Subclasses must implement:
        - `copy_module`: Return the source module whose docstring will be written.
    """

    def stem(self) -> str:
        """Return `"__init__"` as the filename stem."""
        return "__init__"

    def module_path(self) -> Path:
        """Return the target path of the generated `__init__.py`.

        The file lives inside the package directory that mirrors the source
        package within the target project's tree.

        Returns:
            Path to the `__init__.py` that will be written.
        """
        return super().module_path().with_suffix("") / self.filename()

    def import_path(self) -> Path:
        """Return the package directory used to import the managed package.

        Returns:
            Directory of the package whose `__init__.py` this config manages.
        """
        return super().import_path().parent
