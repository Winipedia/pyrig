"""Scaffold shared pytest fixtures for a pyrig-managed project."""

from pyrig.core.strings import kebab_to_snake_case
from pyrig.rig.configs.base.copy_module_docstring import CopyModuleDocstringConfigFile
from pyrig.rig.tests.fixtures import fixtures


def make_fixture(name: str) -> None:
    """Scaffold a new pytest fixture in the project's shared fixtures module.

    Ensures the shared ``fixtures.py`` file exists, then appends a new
    ``@pytest.fixture``-decorated function with the given name. If
    ``import pytest`` is not already present in the file, it is added
    before the new fixture.

    The name is normalized from kebab-case to snake_case so it forms a
    valid Python identifier (e.g. ``"my-new-fixture"`` becomes
    ``"my_new_fixture"``).

    Args:
        name: Name of the fixture in kebab-case or snake_case.
    """
    # create the file if not existent yet
    config_file = CopyModuleDocstringConfigFile.generate_subclass(fixtures)()
    config_file.validate()

    # now add a function with the same name as given to the module
    name = kebab_to_snake_case(name)

    content = config_file.file_content()

    pytest_import = "import pytest"
    if pytest_import not in content:
        content += f"""
{pytest_import}
"""

    content += f'''

@pytest.fixture
def {name}() -> None:
    """This is a pytest fixture."""
'''

    config_file.dump(config_file.split_lines(content))
