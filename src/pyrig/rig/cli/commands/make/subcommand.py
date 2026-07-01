"""Scaffolding logic for extending CLI subcommand modules with new stubs."""

import typer
from pyrig_runtime.core.strings import kebab_to_snake_case
from pyrig_runtime.rig.cli import shared_subcommands, subcommands

from pyrig.rig.configs.base.copy_module_docstring import (
    CopyModuleDocstringConfigFile,
)


def make_subcommand(name: str, *, shared: bool) -> None:
    """Append a new subcommand stub to the project or shared subcommands module.

    The target module file is created if it does not already exist. The command
    name is normalized from kebab-case to snake_case before writing. The appended
    stub is a no-op function with a placeholder docstring, named after the
    normalized command name.

    Args:
        name: Name of the subcommand to create. Accepts kebab-case or snake_case.
        shared: If `True`, targets the shared subcommands module accessible to
            all dependent packages. If `False`, targets the project-specific
            subcommands module.
    """
    # create the file if not existent yet
    config_file = CopyModuleDocstringConfigFile.generate_subclass(
        shared_subcommands if shared else subcommands
    )()
    config_file.validate()
    content = config_file.read_content()

    name = kebab_to_snake_case(name)

    if f"\ndef {name}(" in content:
        typer.echo(f"Subcommand '{name}' already exists.", err=True)
        raise typer.Exit(code=1)

    content += f'''

def {name}() -> None:
    """This is a cli subcommand."""
'''

    config_file.write_content(content)
