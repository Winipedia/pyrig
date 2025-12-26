"""Configuration for the {package_name}/dev/cli/subcommands.py file.

This module provides the SubcommandsConfigFile class for creating a
{package_name}/dev/cli/subcommands.py file where users can define custom
CLI subcommands specific to the current project.

The generated file:
    - Copies the docstring from pyrig.dev.cli.subcommands
    - Provides a place for project-specific CLI subcommands
    - Enables custom CLI functionality for the current project
    - Integrates with pyrig's CLI framework

Project-specific subcommands defined here are automatically discovered and
added to the CLI for the current project only.

See Also:
    pyrig.dev.cli.subcommands
        Source module for the docstring
    pyrig.dev.cli.shared_subcommands
        Shared subcommands available in all projects
"""

from types import ModuleType

from pyrig.dev.cli import subcommands
from pyrig.dev.configs.base.copy_module_docstr import (
    CopyModuleOnlyDocstringConfigFile,
)


class SubcommandsConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Configuration file manager for subcommands.py.

    Generates a {package_name}/dev/cli/subcommands.py file with pyrig's
    subcommands module docstring, providing a starting point for custom CLI
    subcommands specific to the current project.

    The generated file:
        - Contains only the docstring from pyrig.dev.cli.subcommands
        - Provides a place for project-specific CLI subcommands
        - Enables custom CLI functionality
        - Integrates with pyrig's CLI framework

    Shared vs Project-Specific Subcommands:
        - **Project-Specific**: Available only in the current project
          (defined here)
        - **Shared**: Available in all pyrig projects (defined in
          shared_subcommands.py)

    Examples:
        Generate subcommands.py::

            from pyrig.dev.configs.python.subcommands import (
                SubcommandsConfigFile,
            )

            # Creates {package_name}/dev/cli/subcommands.py
            SubcommandsConfigFile()

        Add project-specific subcommands to the generated file::

            # In {package_name}/dev/cli/subcommands.py
            import click

            @click.command()
            def my_command():
                \"\"\"Project-specific command.\"\"\"
                click.echo("Hello from my project!")

    See Also:
        pyrig.dev.cli.subcommands
            Source module for the docstring
        pyrig.dev.configs.python.shared_subcommands.SharedSubcommandsConfigFile
            Shared subcommands available in all projects
        Click documentation: https://click.palletsprojects.com/
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: The pyrig.dev.cli.subcommands module.

        Note:
            Only the docstring is copied; no code is included in the
            generated file.
        """
        return subcommands
