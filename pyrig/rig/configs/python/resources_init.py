"""Configuration for {package_name}/resources/__init__.py.

Generates {package_name}/resources/__init__.py with pyrig.resources docstring for
project resources (data files, templates, etc.).

See Also:
    pyrig.resources
    pyrig.rig.configs.base.init.InitConfigFile
"""

from types import ModuleType

from pyrig import resources
from pyrig.rig.configs.base.init import InitConfigFile


class ResourcesInitConfigFile(InitConfigFile):
    """Manages {package_name}/resources/__init__.py.

    Generates __init__.py for the resources package, copying the docstring
    from pyrig.resources.

    Examples:
        Generate {package_name}/resources/__init__.py::

            ResourcesInitConfigFile.I.validate()

    See Also:
        pyrig.resources
        pyrig.rig.configs.base.init.InitConfigFile
    """

    def src_module(self) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: pyrig.resources module.

        Note:
            Only docstring is copied, no code.
        """
        return resources
