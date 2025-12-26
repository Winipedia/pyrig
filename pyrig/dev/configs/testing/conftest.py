"""Configuration for the pytest conftest.py file.

This module provides the ConftestConfigFile class for creating the
tests/conftest.py file, which configures pytest plugins and makes pyrig's
test fixtures available to the project's test suite.

The generated conftest.py:
    - Imports pyrig's conftest module as a pytest plugin
    - Provides access to pyrig's test fixtures (scoped fixtures for function,
      class, module, package, and session)
    - Sets up pytest hooks and configuration
    - Enables consistent test infrastructure across projects

See Also:
    pyrig.dev.tests.conftest
        pyrig's conftest module with fixtures and plugins
    pytest conftest: https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py
"""

from pyrig.dev.configs.base.py_tests import PythonTestsConfigFile
from pyrig.dev.tests import conftest
from pyrig.src.modules.module import make_obj_importpath


class ConftestConfigFile(PythonTestsConfigFile):
    '''Configuration file manager for tests/conftest.py.

    Generates a conftest.py file that imports pyrig's test infrastructure as
    a pytest plugin. This provides access to pyrig's fixtures, hooks, and
    test utilities.

    The generated file includes:
        - pytest_plugins list with pyrig.dev.tests.conftest
        - Docstring explaining the configuration
        - Warning not to modify manually

    Benefits:
        - Access to pyrig's scoped fixtures (function, class, module, etc.)
        - Consistent test infrastructure across projects
        - Automatic pytest configuration
        - Integration with pyrig's testing utilities

    Examples:
        Generate tests/conftest.py::

            from pyrig.dev.configs.testing.conftest import ConftestConfigFile

            # Creates tests/conftest.py
            ConftestConfigFile()

        The generated file looks like::

            """Pytest configuration for tests.

            This module configures pytest plugins for the test suite...
            """

            pytest_plugins = ["pyrig.dev.tests.conftest"]

    See Also:
        pyrig.dev.tests.conftest
            pyrig's conftest module with fixtures and plugins
        pyrig.dev.configs.base.py_tests.PythonTestsConfigFile
            Base class for test files
    '''

    @classmethod
    def get_content_str(cls) -> str:
        '''Get the conftest.py file content.

        Generates Python code that imports pyrig's conftest module as a pytest
        plugin, making pyrig's fixtures and hooks available to the test suite.

        Returns:
            str: Python code with docstring and pytest_plugins list.

        Examples:
            Returns::

                """Pytest configuration for tests.

                This module configures pytest plugins for the test suite...
                """

                pytest_plugins = ["pyrig.dev.tests.conftest"]
        '''
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

        Validates that the file contains the required pytest_plugins import.
        Allows user modifications as long as the core import is present.

        Returns:
            bool: True if the file contains the required pytest_plugins import,
                False otherwise.

        Note:
            This method reads the file from disk to check its content.
        """
        return super().is_correct() or (
            f'pytest_plugins = ["{make_obj_importpath(conftest)}"]'
            in cls.get_file_content()
        )
