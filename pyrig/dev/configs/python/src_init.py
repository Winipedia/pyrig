"""Configuration for {package_name}/src/__init__.py.

Generates {package_name}/src/__init__.py with pyrig.src docstring for project
source code utilities.

See Also:
    pyrig.src
    pyrig.dev.configs.base.init.InitConfigFile
"""

from types import ModuleType

from pyrig import src
from pyrig.dev.configs.base.init import InitConfigFile


class SrcInitConfigFile(InitConfigFile):
    """Manages {package_name}/src/__init__.py.

    Generates __init__.py with pyrig.src docstring for project source code utilities.

    Examples:
        Generate {package_name}/src/__init__.py::

            SrcInitConfigFile()

        Add utilities::

            # In {package_name}/src/utils.py
            def my_utility_function():
                \"\"\"Utility function.\"\"\"
                return "utility"

    See Also:
        pyrig.src
        pyrig.dev.configs.base.init.InitConfigFile
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: pyrig.src module.

        Note:
            Only docstring is copied, no code.
        """
        return src
