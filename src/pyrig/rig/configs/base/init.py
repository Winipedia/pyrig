"""Base configuration for generating an `__init__.py` file from a source module."""

from pathlib import Path

from pyrig.rig.configs.base.copy_module import (
    CopyModuleConfigFile,
    CopyModuleDocstringConfigFile,
)


class CopyInitConfigFile(CopyModuleConfigFile):
    """Base class for `__init__.py` config files copying a source module's content.

    The generated file is always named `__init__.py` and is placed inside the
    package directory corresponding to the source module in the target project's tree.

    Subclasses must implement:
        - `copy_module`: Return the source module whose content will be copied.
    """

    def import_path(self) -> Path:
        """Return the package directory used to import the managed package.

        Returns:
            Directory of the package whose `__init__.py` this config manages.
        """
        return super().import_path().parent

    def module_path(self) -> Path:
        """Return the target path of the generated `__init__.py`.

        The file lives inside the package directory that mirrors the source
        package within the target project's tree.

        Returns:
            Path to the `__init__.py` that will be written.
        """
        return super().module_path().with_suffix("") / self.filename()

    def stem(self) -> str:
        """Return `"__init__"` as the filename stem."""
        return "__init__"


class CopyInitDocstringConfigFile(CopyInitConfigFile, CopyModuleDocstringConfigFile):
    """Base class for `__init__.py` config files containing a copied module docstring.

    The generated file is always named `__init__.py` and is placed inside the
    package directory corresponding to the source module in the target project's
    tree. Its content is the source module's docstring alone, and it is
    considered correct whenever the scaffolded module has a docstring.

    Subclasses must implement:
        - `copy_module`: Return the source module whose docstring will be copied.
    """
