"""Scaffolding logic for extending CLI subcommand modules with new stubs."""

from pyrig.core.strings import kebab_to_snake_case
from pyrig.rig.cli import shared_subcommands, subcommands
from pyrig.rig.configs.base.copy_module_docstring import CopyModuleDocstringConfigFile


def make_subcommand(name: str, *, shared: bool) -> None:
    """Append a new subcommand stub to the project or shared subcommands module.

    The target file is created if it does not exist yet, initialized with only
    the module docstring copied from the corresponding template module. The
    command name is normalized from kebab-case to snake_case before writing.

    The appended stub has the following form::

        def <name>() -> None:
            \"\"\"This is a cli subcommand.\"\"\"

    Args:
        name: Name of the subcommand to create. Accepts kebab-case or snake_case.
        shared: If ``True``, targets the shared subcommands module accessible to
            all dependent projects. If ``False``, targets the project-specific
            subcommands module.
    """
    # create the file if not existent yet
    config_file = CopyModuleDocstringConfigFile.generate_subclass(
        shared_subcommands if shared else subcommands
    )()
    config_file.validate()

    # now add a function with the same name as given to the module
    name = kebab_to_snake_case(name)

    content = config_file.read_content()

    content += f'''

def {name}() -> None:
    """This is a cli subcommand."""
'''

    config_file.write_content(content)
