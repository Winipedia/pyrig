"""module for the following module path (maybe truncated).

tests.test_pyrig.test_testing.test_tests.test_conftest
"""

from pyrig.rig.tests import conftest


def test_module_docstring() -> None:
    """Test that the module docstrings is generic.

    This is important for CopyModuleOnlyDocstringConfigFile so that the docstring copied
    to the target project's conftest.py is generic and not pyrig-specific.
    """
    assert (
        conftest.__doc__
        == """Pytest configuration for automatic fixture discovery across the pyrig ecosystem.

Registers fixture modules from pyrig and all installed packages that depend on
it as pytest plugins. This makes all discovered fixtures available in every
test module without explicit imports.

The registration walks the ``rig.tests.fixtures`` package path in each
dependent package, collecting all Python modules and registers them as plugins.
"""  # noqa: E501
    )
