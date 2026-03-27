"""Configuration for {package_name}/__init__.py.

Generates {package_name}/__init__.py with pyrig.src docstring for project
source code utilities.
"""

from pathlib import Path
from types import ModuleType

import pyrig
from pyrig.rig.configs.base.init import InitConfigFile
from pyrig.rig.tools.package_manager import PackageManager


class PackageInitConfigFile(InitConfigFile):
    '''Manages {package_name}/__init__.py.

    Generates __init__.py with pyrig docstring for project source code utilities.

    Examples:
        Generate {package_name}/__init__.py::

            PackageInitConfigFile.I.validate()

        Add utilities::

            # In {package_name}/utils.py
            def my_utility_function():
                """Utility function."""
                return "utility"

    '''

    def parent_path(self) -> Path:
        """Special case to because the parent is the cwd, not a subdir.

        So normal parent path logic would return pyrig anyway instead of
        the actual current projects package name.
        """
        return Path(PackageManager.I.package_name())

    def create_file(self) -> None:
        """Create main.py by copying the `pyrig.main` module.

        Also delete root-level main.py if it exists to clean up legacy
        files from ``uv init``.
        """
        super().create_file()
        self.delete_root_main()

    def src_module(self) -> ModuleType:
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
