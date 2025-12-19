"""Configuration for the pytest conftest.py file.

This module provides the ConftestConfigFile class for creating
the tests/conftest.py file that configures pytest plugins.
"""

from pyrig.dev.configs.base.base import PythonTestsConfigFile
from pyrig.src.modules.module import make_obj_importpath


class ConftestConfigFile(PythonTestsConfigFile):
    """Configuration file manager for conftest.py.

    Creates a conftest.py that imports pyrig's test fixtures and
    plugins for consistent test infrastructure.
    """

    @classmethod
    def get_content_str(cls) -> str:
        """Get the conftest.py content.

        Returns:
            Python code that imports pyrig's conftest as a pytest plugin.
        """
        from pyrig.dev.tests import conftest  # noqa: PLC0415

        return f'''"""Pytest configuration for tests.

This module configures pytest plugins for the test suite, setting up the necessary
fixtures and hooks for the different
test scopes (function, class, module, package, session).
It also import custom plugins from tests/base/scopes.
This file should not be modified manually.
"""

pytest_plugins = ["{make_obj_importpath(conftest)}"]
'''

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the conftest.py file is valid.

        Allows modifications as long as the file contains the required import.

        Returns:
            True if the file has required structure.
        """
        from pyrig.dev.tests import conftest  # noqa: PLC0415

        return super().is_correct() or (
            f'pytest_plugins = ["{make_obj_importpath(conftest)}"]'
            in cls.get_file_content()
        )
