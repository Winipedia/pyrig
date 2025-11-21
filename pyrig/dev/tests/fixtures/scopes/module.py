"""Module-level test fixtures and utilities.

These fixtures in this module are automatically applied to all test modules
through pytest's autouse mechanism. Pyrig automatically adds this module to
pytest_plugins in conftest.py. However you still have decorate the fixture
with @autouse_module_fixture from pyrig.src.testing.fixtures or with pytest's
autouse mechanism @pytest.fixture(scope="module", autouse=True).
"""

from typing import TYPE_CHECKING

import pytest

from pyrig.src.testing.fixtures import autouse_module_fixture
from pyrig.src.testing.utils import assert_no_untested_objs

if TYPE_CHECKING:
    from types import ModuleType


@autouse_module_fixture
def assert_all_funcs_and_classes_tested(request: pytest.FixtureRequest) -> None:
    """Verify that all functions and classes in a module have corresponding tests.

    This fixture runs automatically for each test module and checks that every
    function and class defined in the corresponding source module has a test
    function or class defined in the test module.

    Args:
        request: The pytest fixture request object containing the current module

    Raises:
        AssertionError: If any function or class in the source module lacks a test

    """
    module: ModuleType = request.module
    assert_no_untested_objs(module)
