"""Configuration for {package_name}/__init__.py.

Generates {package_name}/__init__.py with pyrig.src docstring for project
source code utilities.
"""

from pathlib import Path
from types import ModuleType

import pyrig
from pyrig.rig.configs.base.init import InitConfigFile


class PackageInitConfigFile(InitConfigFile):
    '''Manages {package_name}/__init__.py.

    Generates __init__.py with pyrig docstring for project source code utilities.

    We need to make sure the docstring is generic and not pyrig specific
    since it will be copied into the user's project.
    The docstring should be minimal and work for any project.

    Examples:
        Generate {package_name}/__init__.py::

            PackageInitConfigFile.I.validate()

        Add utilities::

            # In {package_name}/utils.py
            def my_utility_function():
                """Utility function."""
                return "utility"

    '''

    def create_file(self) -> None:
        """Create main.py by copying the `pyrig.main` module.

        Also delete root-level main.py if it exists to clean up legacy
        files from ``uv init``.
        """
        super().create_file()
        self.delete_root_main()

    def copy_module(self) -> ModuleType:
        """Return the `pyrig` module."""
        return pyrig

    def delete_root_main(self) -> None:
        """Delete root-level main.py if it exists.

        Note:
            Called automatically during `create_file` to clean up legacy
            files from ``uv init``.
        """
        root_main_path = Path("main.py")
        if root_main_path.exists():
            root_main_path.unlink()
