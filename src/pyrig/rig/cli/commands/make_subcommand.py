"""Helpers to scaffold new CLI subcommand function stubs."""

from pyrig.core.string_ import kebab_to_snake_case
from pyrig.rig.cli import shared_subcommands, subcommands
from pyrig.rig.configs.base.copy_module_docstr import CopyModuleOnlyDocstringConfigFile


def make_subcommand(name: str, *, shared: bool) -> None:
    """Create a new subcommand function in the selected subcommands module.

    The function name is normalized from kebab-case to snake_case and appended
    as a stub to either the project-specific subcommands module or the shared
    subcommands module.

    Args:
        name: Name of the command to create.
        shared: Whether to write the subcommand into shared subcommands.
    """
    # create the file if not existent yet
    config_file = CopyModuleOnlyDocstringConfigFile.generate_subclass(
        shared_subcommands if shared else subcommands
    )()
    config_file.validate()

    # now add a function with the same name as given to the module
    name = kebab_to_snake_case(name)

    content = config_file.file_content()

    content += f'''

def {name}() -> None:
    """This is a cli subcommand."""
'''

    config_file.dump(content.splitlines())
