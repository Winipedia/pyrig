"""Configuration for the {package_name}/src/__init__.py file.

This module provides the SrcInitConfigFile class for creating the
{package_name}/src/__init__.py file that mirrors pyrig's src package
structure.

The generated file:
    - Copies the docstring from pyrig.src
    - Provides a place for project source code utilities
    - Follows pyrig's package structure conventions
    - Enables shared utility code organization

See Also:
    pyrig.src
        Source module for the docstring
    pyrig.dev.configs.base.init.InitConfigFile
        Base class for __init__.py file generation
"""

from types import ModuleType

from pyrig import src
from pyrig.dev.configs.base.init import InitConfigFile


class SrcInitConfigFile(InitConfigFile):
    """Configuration file manager for {package_name}/src/__init__.py.

    Generates a {package_name}/src/__init__.py file with pyrig's src module
    docstring, providing a starting point for project source code utilities.

    The generated file:
        - Contains only the docstring from pyrig.src
        - Provides a place for shared utility code
        - Follows pyrig's package structure
        - Enables code organization and reuse

    Use Cases:
        - Define utility functions and classes
        - Create shared modules for the project
        - Organize helper code
        - Provide common functionality

    Examples:
        Generate {package_name}/src/__init__.py::

            from pyrig.dev.configs.python.src_init import SrcInitConfigFile

            # Creates {package_name}/src/__init__.py
            SrcInitConfigFile()

        Add utilities to the generated package::

            # In {package_name}/src/utils.py
            def my_utility_function():
                \"\"\"Utility function.\"\"\"
                return "utility"

    See Also:
        pyrig.src
            Source module for the docstring
        pyrig.dev.configs.base.init.InitConfigFile
            Base class for __init__.py generation
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: The pyrig.src module.

        Note:
            Only the docstring is copied; no code is included in the
            generated file.
        """
        return src
