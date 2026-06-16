"""Configuration for generating the top-level package ``__init__.py`` file.

Produces ``src/{package_name}/__init__.py`` with a generic module docstring.
"""

from types import ModuleType

import pyrig
from pyrig.rig.configs.base.init import InitConfigFile


class PackageInitConfigFile(InitConfigFile):
    """Generates the project's top-level package ``__init__.py``.

    Writes ``src/{package_name}/__init__.py`` using the docstring from the ``pyrig``
    root module. That docstring is intentionally generic so it reads correctly
    in any scaffolded project's top-level package.
    """

    def copy_module(self) -> ModuleType:
        """Return the ``pyrig`` root module as the docstring source.

        The ``pyrig`` module's docstring is written into the generated
        ``__init__.py``. It reads ``"The top-level package for the project."``,
        which is intentionally generic so it applies to any scaffolded project.

        Returns:
            The ``pyrig`` root module.
        """
        return pyrig
