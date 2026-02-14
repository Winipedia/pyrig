"""Configuration for {package_name}/rig/tools/__init__.py.

Generates {package_name}/rig/tools/__init__.py with pyrig.rig.tools docstring
for tool wrapper modules (uv, ruff, pyinstaller, etc.).

See Also:
    pyrig.rig.tools
    pyrig.rig.configs.base.init.InitConfigFile
"""

from types import ModuleType

from pyrig.rig import tools
from pyrig.rig.configs.base.base import Priority
from pyrig.rig.configs.base.init import InitConfigFile


class ToolsInitConfigFile(InitConfigFile):
    """Manages {package_name}/rig/tools/__init__.py.

    Generates __init__.py for the rig/tools package, copying the docstring
    from pyrig.rig.tools.

    Examples:
        Generate {package_name}/rig/tools/__init__.py::

            ToolsInitConfigFile.validate()

    See Also:
        pyrig.rig.tools
        pyrig.rig.configs.base.init.InitConfigFile
    """

    @classmethod
    def priority(cls) -> float:
        """Return `Priority.LOW` to trigger validation earlier than default."""
        return Priority.LOW

    @classmethod
    def src_module(cls) -> ModuleType:
        """Return the `pyrig.rig.tools` module."""
        return tools
