"""Configuration for the {package_name}/resources/__init__.py file.

This module provides the ResourcesInitConfigFile class for creating the
{package_name}/resources/__init__.py file that mirrors pyrig's resources
package structure.

The generated file:
    - Copies the docstring from pyrig.resources
    - Provides a place for project resources (data files, templates, etc.)
    - Follows pyrig's package structure conventions
    - Enables resource file management

See Also:
    pyrig.resources
        Source module for the docstring
    pyrig.dev.configs.base.init.InitConfigFile
        Base class for __init__.py file generation
"""

from types import ModuleType

from pyrig import resources
from pyrig.dev.configs.base.init import InitConfigFile


class ResourcesInitConfigFile(InitConfigFile):
    """Configuration file manager for {package_name}/resources/__init__.py.

    Generates a {package_name}/resources/__init__.py file with pyrig's
    resources module docstring, providing a starting point for project
    resource files.

    The generated file:
        - Contains only the docstring from pyrig.resources
        - Provides a place for data files, templates, configs, etc.
        - Follows pyrig's package structure
        - Enables resource file organization

    Use Cases:
        - Store data files (JSON, CSV, etc.)
        - Store template files (Jinja2, etc.)
        - Store configuration files
        - Organize non-code project assets

    Examples:
        Generate {package_name}/resources/__init__.py::

            from pyrig.dev.configs.python.resources_init import (
                ResourcesInitConfigFile,
            )

            # Creates {package_name}/resources/__init__.py
            ResourcesInitConfigFile()

        Add resources to the generated directory::

            # {package_name}/resources/data.json
            {{"key": "value"}}

            # {package_name}/resources/template.txt
            Hello {{name}}!

    See Also:
        pyrig.resources
            Source module for the docstring
        pyrig.dev.configs.base.init.InitConfigFile
            Base class for __init__.py generation
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: The pyrig.resources module.

        Note:
            Only the docstring is copied; no code is included in the
            generated file.
        """
        return resources
