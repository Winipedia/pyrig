"""module for the following module path (maybe truncated).

tests.base.scopes.session
"""

import re

from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.module import to_path
from pyrig.src.project.poetry import dev_deps
from pyrig.src.project.poetry.dev_deps import DEV_DEPENDENCIES
from pyrig.src.testing.assertions import assert_with_msg
from pyrig.src.testing.fixtures import autouse_session_fixture


@autouse_session_fixture
def assert_dev_dependencies_config_is_correct() -> None:
    """Verify that the dev dependencies in consts.py are correct.

    If not it dumps the correct config to consts.py.
    """
    expected_dev_deps = PyprojectConfigFile.get_dev_dependencies()
    actual_dev_deps = DEV_DEPENDENCIES

    correct = expected_dev_deps == actual_dev_deps
    if correct:
        return

    path = to_path(module_name=dev_deps, is_package=False)
    content = path.read_text()
    # replace DEV_DEPENDENCIES = {.*} with the correct value with re
    pattern = r"DEV_DEPENDENCIES: dict\[str, str \| dict\[str, str\]\] = \{.*?\}"

    replacement = (
        f"DEV_DEPENDENCIES: dict[str, str | dict[str, str]] = {expected_dev_deps}"
    )

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    path.write_text(new_content)

    assert_with_msg(
        correct,
        "Dev dependencies in consts.py are not correct. "
        "Corrected the file. Please verify the changes.",
    )
