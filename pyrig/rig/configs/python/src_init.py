"""Configuration for {package_name}/src/__init__.py.

Generates {package_name}/src/__init__.py with pyrig.src docstring for project
source code utilities.

See Also:
    pyrig.src
    pyrig.rig.configs.base.init.InitConfigFile
"""

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

    def src_module(self) -> ModuleType:
        """Return the `pyrig.src` module."""
        return src

    def src_module(self) -> ModuleType: