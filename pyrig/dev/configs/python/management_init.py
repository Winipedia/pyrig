"""Configuration for {package_name}/dev/management/__init__.py.

Generates {package_name}/dev/management/__init__.py with pyrig.dev.management docstring
for tool wrapper modules (uv, ruff, pyinstaller, etc.).

See Also:
    pyrig.dev.management
    pyrig.dev.configs.base.init.InitConfigFile
"""

from types import ModuleType

from pyrig.dev import management
from pyrig.dev.configs.base.init import InitConfigFile


class ManagementInitConfigFile(InitConfigFile):
    """Manages {package_name}/dev/management/__init__.py.

    Generates __init__.py with pyrig.dev.management docstring for tool wrapper
    modules that provide Python interfaces to CLI tools.

    Examples:
        Generate {package_name}/dev/management/__init__.py::

            ManagementInitConfigFile()

        Add tool wrappers::

            # {package_name}/dev/management/mytool.py
            class MyTool(Tool):
                '''MyTool wrapper.'''
                @classmethod
                def name(cls) -> str:
                    return "mytool"
                @classmethod
                def get_run_args(cls, *args: str) -> Args:
                    return cls.get_args("run", *args)

    See Also:
        pyrig.dev.management
        pyrig.dev.configs.base.init.InitConfigFile
    """

    @classmethod
    def get_priority(cls) -> float:
        """Get the priority for this config file.

        Returns:
            float: 10.0 (ensures management directory exists before other files use it).
        """
        return 10

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: pyrig.dev.management module.

        Note:
            Only docstring is copied, no code.
        """
        return management
