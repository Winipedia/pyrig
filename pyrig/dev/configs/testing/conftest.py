"""Configuration for the pytest conftest.py file.

This module provides the ConftestConfigFile class for creating
the tests/conftest.py file that configures pytest plugins.
"""

from subprocess import CompletedProcess  # nosec: B404

from pyrig.dev.configs.base.base import PythonTestsConfigFile
from pyrig.src.modules.module import make_obj_importpath
from pyrig.src.os.os import run_subprocess
from pyrig.src.project.mgt import PROJECT_MGT_RUN_ARGS


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
    def run_tests(cls, *, check: bool = True) -> CompletedProcess[str]:
        """Run the project's test suite using pytest.

        Args:
            check: Whether to raise on test failure.

        Returns:
            The completed process result.
        """
        return run_subprocess([*PROJECT_MGT_RUN_ARGS, "pytest"], check=check)
