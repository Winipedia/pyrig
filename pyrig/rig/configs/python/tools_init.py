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

    Generates __init__.py with pyrig.rig.tools docstring for tool wrapper
    modules that provide Python interfaces to CLI tools.

    Examples:
        Generate {package_name}/rig/tools/__init__.py::

            ToolsInitConfigFile()

        Add tool wrappers::

            # {package_name}/rig/tools/mytool.py
            class MyTool(Tool):
                '''MyTool wrapper.'''
                @classmethod
                def name(cls) -> str:
                    return "mytool"
                @classmethod
                def get_run_args(cls, *args: str) -> Args:
                    return cls.get_args("run", *args)

    See Also:
        pyrig.rig.tools
        pyrig.rig.configs.base.init.InitConfigFile
    """

    @classmethod
    def get_priority(cls) -> float:
        """Get the priority for this config file.

        Returns:
            float: 10.0 (ensures tools directory exists before other files use it).
        """
        return Priority.LOW

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: pyrig.rig.tools module.

        Note:
            Only docstring is copied, no code.
        """
        return tools
