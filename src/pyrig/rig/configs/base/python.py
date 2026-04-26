r"""Abstract base class for Python source file configuration.

Provides ``PythonConfigFile`` as the base for all generated ``.py`` files,
setting a fixed ``"py"`` extension on top of the string-based config system.
"""

from pyrig.rig.configs.base.string_ import StringConfigFile


class PythonConfigFile(StringConfigFile):
    """Abstract base class for Python (``.py``) source files.

    Fixes the file extension to ``"py"`` and inherits all content validation,
    file I/O, and update logic from ``StringConfigFile``.

    Subclasses must implement:
        - ``parent_path``: The directory that will contain the ``.py`` file.
        - ``lines``: The Python source lines required to be present in the file.

    Example:
        Define a concrete Python config file::

            from pathlib import Path
            from pyrig.rig.configs.base.python import PythonConfigFile

            class MyPythonFile(PythonConfigFile):

                def parent_path(self) -> Path:
                    return Path("src")

                def lines(self) -> list[str]:
                    return ["from typing import Any", "import sys"]
    """

    def extension(self) -> str:
        """Return the file extension for Python source files.

        Returns:
            ``"py"``
        """
        return "py"
