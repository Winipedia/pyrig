"""Configuration for generating the top-level package ``__init__.py`` file.

Produces ``{package_name}/__init__.py`` with a generic module docstring and
removes the ``main.py`` file that ``uv init`` places in the project root.
"""

from pathlib import Path
from types import ModuleType

import pyrig
from pyrig.rig.configs.base.init import InitConfigFile


class PackageInitConfigFile(InitConfigFile):
    """Generates the project's top-level package ``__init__.py``.

    Writes ``{package_name}/__init__.py`` using the docstring from the ``pyrig``
    root module. That docstring is intentionally generic so it reads correctly
    in any scaffolded project's top-level package.

    After writing the file, removes the root-level ``main.py`` that ``uv init``
    creates as boilerplate, since pyrig-managed projects do not use it.

    Example:
        >>> PackageInitConfigFile.I.validate()
    """

    def create_file(self) -> None:
        """Generate ``{package_name}/__init__.py`` and remove the root ``main.py``.

        Delegates file creation to the parent implementation, then removes
        ``main.py`` from the project root if it exists.
        """
        super().create_file()
        self.delete_root_main()

    def copy_module(self) -> ModuleType:
        """Return the ``pyrig`` root module as the docstring source.

        The ``pyrig`` module's docstring is written into the generated
        ``__init__.py``. It reads ``"The top-level package for the project."``,
        which is intentionally generic so it applies to any scaffolded project.

        Returns:
            The ``pyrig`` root module.
        """
        return pyrig

    def delete_root_main(self) -> None:
        """Remove ``main.py`` from the project root if it exists.

        ``uv init`` places a ``main.py`` in the project root as a starter
        script. Pyrig-managed projects do not use it, so this cleanup step
        removes it after the package ``__init__.py`` is generated.
        """
        root_main_path = Path("main.py")
        if root_main_path.exists():
            root_main_path.unlink()
