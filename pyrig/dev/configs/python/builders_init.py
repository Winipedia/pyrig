"""Configuration for the {package_name}/dev/builders/__init__.py file.

This module provides the BuildersInitConfigFile class for creating the
{package_name}/dev/builders/__init__.py file that mirrors pyrig's builders
package structure.

The generated file:
    - Copies the docstring from pyrig.dev.builders
    - Provides a place for custom builder classes
    - Follows pyrig's package structure conventions
    - Enables project-specific artifact builders

See Also:
    pyrig.dev.builders
        Source module for the docstring
    pyrig.dev.configs.base.init.InitConfigFile
        Base class for __init__.py file generation
"""

from types import ModuleType

from pyrig.dev import builders
from pyrig.dev.configs.base.init import InitConfigFile


class BuildersInitConfigFile(InitConfigFile):
    '''Configuration file manager for {package_name}/dev/builders/__init__.py.

    Generates a {package_name}/dev/builders/__init__.py file with pyrig's
    builders module docstring, providing a starting point for custom builder
    classes.

    The generated file:
        - Contains only the docstring from pyrig.dev.builders
        - Provides a place for project-specific builders
        - Follows pyrig's package structure
        - Enables custom artifact building logic

    Use Cases:
        - Define custom build processes
        - Create project-specific artifact builders
        - Extend pyrig's builder functionality
        - Organize build-related code

    Examples:
        Generate {package_name}/dev/builders/__init__.py::

            from pyrig.dev.configs.python.builders_init import (
                BuildersInitConfigFile,
            )

            # Creates {package_name}/dev/builders/__init__.py
            BuildersInitConfigFile()

        Add custom builders to the generated file::

            # In {package_name}/dev/builders/__init__.py
            from pyrig.dev.builders.base.base import Builder

            class CustomBuilder(Builder):
                """Custom artifact builder."""
                pass

    See Also:
        pyrig.dev.builders
            Source module for the docstring
        pyrig.dev.configs.base.init.InitConfigFile
            Base class for __init__.py generation
    '''

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: The pyrig.dev.builders module.

        Note:
            Only the docstring is copied; no code is included in the
            generated file.
        """
        return builders
