"""Configuration for the {package_name}/dev/cli/shared_subcommands.py file.

This module provides the SharedSubcommandsConfigFile class for creating a
{package_name}/dev/cli/shared_subcommands.py file where users can define
custom CLI subcommands that are available in all pyrig projects.

The generated file:
    - Copies the docstring from pyrig.dev.cli.shared_subcommands
    - Provides a place for shared CLI subcommands
    - Enables custom CLI functionality across all pyrig projects
    - Integrates with pyrig's CLI framework

Shared subcommands defined here are automatically discovered and added to
the CLI for all pyrig projects.

See Also:
    pyrig.dev.cli.shared_subcommands
        Source module for the docstring
    pyrig.dev.cli.subcommands
        Project-specific subcommands
"""

from types import ModuleType

from pyrig.dev.cli import shared_subcommands
from pyrig.dev.configs.base.copy_module_docstr import (
    CopyModuleOnlyDocstringConfigFile,
)


class SharedSubcommandsConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Configuration file manager for shared_subcommands.py.

    Generates a {package_name}/dev/cli/shared_subcommands.py file with pyrig's
    shared_subcommands module docstring, providing a starting point for custom
    CLI subcommands that are shared across all pyrig projects.

    The generated file:
        - Contains only the docstring from pyrig.dev.cli.shared_subcommands
        - Provides a place for shared CLI subcommands
        - Enables custom CLI functionality
        - Integrates with pyrig's CLI framework

    Shared vs Project-Specific Subcommands:
        - **Shared**: Available in all pyrig projects (defined here)
        - **Project-Specific**: Available only in the current project
          (defined in subcommands.py)

    Examples:
        Generate shared_subcommands.py::

            from pyrig.dev.configs.python.shared_subcommands import (
                SharedSubcommandsConfigFile,
            )

            # Creates {package_name}/dev/cli/shared_subcommands.py
            SharedSubcommandsConfigFile()

        Add shared subcommands to the generated file::

            # In {package_name}/dev/cli/shared_subcommands.py
            def my_shared_command() -> None:
                \"\"\"Shared command available in all projects.\"\"\"
                from myproject.utils import shared_functionality
                shared_functionality()

        The function is automatically discovered and registered as a Typer
        command by pyrig's CLI system. No decorators needed.

    See Also:
        pyrig.dev.cli.shared_subcommands
            Source module for the docstring
        pyrig.dev.configs.python.subcommands.SubcommandsConfigFile
            Project-specific subcommands
        pyrig.dev.cli.cli.add_shared_subcommands
            Function that discovers and registers shared subcommands
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: The pyrig.dev.cli.shared_subcommands module.

        Note:
            Only the docstring is copied; no code is included in the
            generated file.
        """
        return shared_subcommands
