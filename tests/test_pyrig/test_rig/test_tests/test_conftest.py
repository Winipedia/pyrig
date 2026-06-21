"""module for the following module path (maybe truncated).

tests.test_pyrig.test_testing.test_tests.test_conftest
"""

from pyrig_fixtures.rig.tests.fixtures import fixtures

from pyrig.rig.tests import conftest


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


def test_pytest_plugins() -> None:
    """Test function."""
    plugins = conftest.pytest_plugins
    assert fixtures.__name__ in plugins
