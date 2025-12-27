"""Configuration for {package_name}/resources/__init__.py.

Generates {package_name}/resources/__init__.py with pyrig.resources docstring for
project resources (data files, templates, etc.).

See Also:
    pyrig.resources
    pyrig.dev.configs.base.init.InitConfigFile
"""

from types import ModuleType

from pyrig import resources
from pyrig.dev.configs.base.init import InitConfigFile


class ResourcesInitConfigFile(InitConfigFile):
    """Manages {package_name}/resources/__init__.py.

    Generates __init__.py with pyrig.resources docstring for project resource files
    (data files, templates, configs, etc.).

    Examples:
        Generate {package_name}/resources/__init__.py::

            ResourcesInitConfigFile()

        Add resources::

            # {package_name}/resources/data.json
            {{"key": "value"}}

            # {package_name}/resources/template.txt
            Hello {{name}}!

    See Also:
        pyrig.resources
        pyrig.dev.configs.base.init.InitConfigFile
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: pyrig.resources module.

        Note:
            Only docstring is copied, no code.
        """
        return resources
