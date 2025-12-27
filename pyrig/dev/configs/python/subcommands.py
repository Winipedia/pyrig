"""Configuration for {package_name}/dev/cli/subcommands.py.

Generates {package_name}/dev/cli/subcommands.py with pyrig.dev.cli.subcommands
docstring for custom CLI subcommands specific to the current project.

See Also:
    pyrig.dev.cli.subcommands
    pyrig.dev.cli.shared_subcommands
"""

from types import ModuleType

from pyrig.dev.cli import subcommands
from pyrig.dev.configs.base.copy_module_docstr import (
    CopyModuleOnlyDocstringConfigFile,
)


class SubcommandsConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Manages subcommands.py.

    Generates {package_name}/dev/cli/subcommands.py with pyrig.dev.cli.subcommands
    docstring for custom CLI subcommands specific to the current project.

    Examples:
        Generate subcommands.py::

            SubcommandsConfigFile()

        Add project-specific subcommands::

            # In {package_name}/dev/cli/subcommands.py
            def my_command() -> None:
                \"\"\"Project-specific command.\"\"\"
                from myproject.core import do_something
                do_something()

        Functions are auto-discovered and registered as Typer commands.

    See Also:
        pyrig.dev.cli.subcommands
        pyrig.dev.configs.python.shared_subcommands.SharedSubcommandsConfigFile
        pyrig.dev.cli.cli.add_subcommands
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: pyrig.dev.cli.subcommands module.

        Note:
            Only docstring is copied, no code.
        """
        return subcommands
