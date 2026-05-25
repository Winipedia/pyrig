"""module for the following module path (maybe truncated).

tests.test_pyrig.test_testing.test_tests.test_conftest
"""

from types import SimpleNamespace

import pytest

from pyrig.rig.tests import conftest
from pyrig.rig.tests.conftest import pytest_sessionfinish


def test_module_docstring() -> None:
    """Test that the module docstrings is generic.

    This is important for CopyModuleDocstringConfigFile so that the docstring copied
    to the target project's conftest.py is generic and not pyrig-specific.
    """
    assert (
        conftest.__doc__
        == """Pytest configuration for automatic fixture discovery across the pyrig ecosystem.

Registers fixture modules from pyrig and all installed packages that depend on
it as pytest plugins. This makes all discovered fixtures available in every
test module without explicit imports.

The registration walks the ``<project_name>.rig.tests.fixtures`` package path in
pyrig and all pyrig dependent packages, collecting all Python modules except
``__init__.py`` modules and registers them as plugins.
"""  # noqa: E501
    )


def test_pytest_sessionfinish() -> None:
    """Test func."""
    session = SimpleNamespace(exitstatus=None)

    pytest_sessionfinish(
        session,  # ty:ignore[invalid-argument-type]
        pytest.ExitCode.NO_TESTS_COLLECTED,
    )

    assert session.exitstatus == pytest.ExitCode.OK
