"""Configuration for {package_name}/src/__init__.py.

Generates {package_name}/src/__init__.py with pyrig.src docstring for project
source code utilities.

See Also:
    pyrig.src
    pyrig.rig.configs.base.init.InitConfigFile
"""

from pathlib import Path
from types import ModuleType

from pyrig import src
from pyrig.rig.configs.base.init import InitConfigFile


class SrcInitConfigFile(InitConfigFile):
    """Manages {package_name}/src/__init__.py.

    Generates __init__.py with pyrig.src docstring for project source code utilities.

    Examples:
        Generate {package_name}/src/__init__.py::

            SrcInitConfigFile.I.validate()

        Add utilities::

            # In {package_name}/src/utils.py
            def my_utility_function():
                \"\"\"Utility function.\"\"\"
                return "utility"

    See Also:
        pyrig.src
        pyrig.rig.configs.base.init.InitConfigFile
    """

    def create_file(self) -> None:
        """Create main.py by copying the `pyrig.main` module.

        Also delete root-level main.py if it exists to clean up legacy
        files from ``uv init``.
        """
        super().create_file()
        self.delete_root_main()

    def src_module(self) -> ModuleType:
        """Return the `pyrig.src` module."""
        return src

    def delete_root_main(self) -> None:
        """Delete root-level main.py if it exists.

        Note:
            Called automatically during `create_file` to clean up legacy
            files from ``uv init``.
        """
        root_main_path = Path("main.py")
        if root_main_path.exists():
            root_main_path.unlink()
