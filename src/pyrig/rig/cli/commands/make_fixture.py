"""Helpers to scaffold new shared pytest fixture."""

from pyrig.core.string_ import kebab_to_snake_case
from pyrig.rig.configs.base.copy_module_docstr import CopyModuleOnlyDocstringConfigFile
from pyrig.rig.tests.fixtures import fixtures


def make_fixture(name: str) -> None:
    """Create a new pytest fixture scaffold in the shared fixtures module."""
    # create the file if not existent yet
    config_file = CopyModuleOnlyDocstringConfigFile.generate_subclass(fixtures)()
    config_file.validate()

    # now add a function with the same name as given to the module
    name = kebab_to_snake_case(name)

    content = config_file.file_content()

    pytest_import = "import pytest"
    if pytest_import not in content:
        content += f"""

{pytest_import}"""

    content += f'''

@pytest.fixture
def {name}() -> None:
    """This is a pytest fixture."""
'''

    config_file.dump(content.splitlines())
