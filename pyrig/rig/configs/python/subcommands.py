"""Configuration for {package_name}/rig/cli/subcommands.py.

Generates {package_name}/rig/cli/subcommands.py with pyrig.rig.cli.subcommands
docstring for custom CLI subcommands specific to the current project.

See Also:
    pyrig.rig.cli.subcommands
    pyrig.rig.cli.shared_subcommands
"""

from types import ModuleType

from pyrig.rig.cli import subcommands
from pyrig.rig.configs.base.copy_module_docstr import (
    CopyModuleOnlyDocstringConfigFile,
)


class SubcommandsConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Manages subcommands.py.

    Generates {package_name}/rig/cli/subcommands.py with pyrig.rig.cli.subcommands
    docstring for custom CLI subcommands specific to the current project.

    Examples:
        Generate subcommands.py::

            SubcommandsConfigFile.I.validate()

        Add project-specific subcommands::

            # In {package_name}/rig/cli/subcommands.py
            def my_command() -> None:
                \"\"\"Project-specific command.\"\"\"
                ...

    Note:
        Functions are auto-discovered and registered as Typer commands.

    See Also:
        pyrig.rig.cli.subcommands
        pyrig.rig.configs.python.shared_subcommands.SharedSubcommandsConfigFile
        pyrig.rig.cli.cli.add_subcommands
    """

    def src_module(self) -> ModuleType:
        """Return the `pyrig.rig.cli.subcommands` module."""
        return subcommands
