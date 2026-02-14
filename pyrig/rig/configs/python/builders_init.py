"""Configuration for {package_name}/rig/builders/__init__.py.

Generates {package_name}/rig/builders/__init__.py with pyrig.rig.builders docstring,
providing a starting point for custom builder classes.

See Also:
    pyrig.rig.builders
    pyrig.rig.configs.base.init.InitConfigFile
"""

from types import ModuleType

from pyrig.rig import builders
from pyrig.rig.configs.base.init import InitConfigFile


class BuildersInitConfigFile(InitConfigFile):
    '''Manages {package_name}/rig/builders/__init__.py.

    Generates __init__.py with pyrig.rig.builders docstring for custom builder classes.

    Examples:
        Generate {package_name}/rig/builders/__init__.py::

            BuildersInitConfigFile.validate()

        Add custom builders::

            # In {package_name}/rig/builders/__init__.py
            from pyrig.rig.builders.base.base import BuilderConfigFile

            class CustomBuilder(BuilderConfigFile):
                """Custom artifact builder."""
                pass

    See Also:
        pyrig.rig.builders
        pyrig.rig.configs.base.init.InitConfigFile
    '''

    @classmethod
    def src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            The `pyrig.rig.builders` module.

        Note:
            Only docstring is copied, no code.
        """
        return builders
