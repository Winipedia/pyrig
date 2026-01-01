"""Configuration for {package_name}/dev/builders/__init__.py.

Generates {package_name}/dev/builders/__init__.py with pyrig.dev.builders docstring,
providing a starting point for custom builder classes.

See Also:
    pyrig.dev.builders
    pyrig.dev.configs.base.init.InitConfigFile
"""

from types import ModuleType

from pyrig.dev import builders
from pyrig.dev.configs.base.init import InitConfigFile


class BuildersInitConfigFile(InitConfigFile):
    '''Manages {package_name}/dev/builders/__init__.py.

    Generates __init__.py with pyrig.dev.builders docstring for custom builder classes.

    Examples:
        Generate {package_name}/dev/builders/__init__.py::

            BuildersInitConfigFile()

        Add custom builders::

            # In {package_name}/dev/builders/__init__.py
            from pyrig.dev.builders.base.base import BuilderConfigFile

            class CustomBuilder(BuilderConfigFile):
                """Custom artifact builder."""
                pass

    See Also:
        pyrig.dev.builders
        pyrig.dev.configs.base.init.InitConfigFile
    '''

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: pyrig.dev.builders module.

        Note:
            Only docstring is copied, no code.
        """
        return builders
