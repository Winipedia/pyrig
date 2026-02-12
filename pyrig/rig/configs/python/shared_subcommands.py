"""Configuration for {package_name}/rig/cli/shared_subcommands.py.

Generates {package_name}/rig/cli/shared_subcommands.py
with pyrig.rig.cli.shared_subcommands
docstring for custom CLI subcommands available in all pyrig projects.

See Also:
    pyrig.rig.cli.shared_subcommands
    pyrig.rig.cli.subcommands
"""

from types import ModuleType

from pyrig.rig.cli import shared_subcommands
from pyrig.rig.configs.base.copy_module_docstr import (
    CopyModuleOnlyDocstringConfigFile,
)


class SharedSubcommandsConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Manages shared_subcommands.py.

    Generates {package_name}/rig/cli/shared_subcommands.py
    with pyrig.rig.cli.shared_subcommands docstring for custom CLI subcommands
    shared across all pyrig projects.

    Examples:
        Generate shared_subcommands.py::

            SharedSubcommandsConfigFile()

        Add shared subcommands::

            # In {package_name}/rig/cli/shared_subcommands.py
            def my_shared_command() -> None:
                \"\"\"Shared command available in all projects.\"\"\"
                from myproject.utils import shared_functionality
                shared_functionality()

        Functions are auto-discovered and registered as Typer commands.

    See Also:
        pyrig.rig.cli.shared_subcommands
        pyrig.rig.configs.python.subcommands.SubcommandsConfigFile
        pyrig.rig.cli.cli.add_shared_subcommands
    """

    @classmethod
    def src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: pyrig.rig.cli.shared_subcommands module.

        Note:
            Only docstring is copied, no code.
        """
        return shared_subcommands
