"""Config utilities for conftest.py."""

from subprocess import CompletedProcess  # nosec: B404

from pyrig.dev.configs.base.base import PythonTestsConfigFile
from pyrig.src.modules.module import make_obj_importpath
from pyrig.src.os.os import run_subprocess


class ConftestConfigFile(PythonTestsConfigFile):
    """Config file for conftest.py."""

    @classmethod
    def get_content_str(cls) -> str:
        """Get the config content."""
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
        """Run the tests."""
        return run_subprocess(["poetry", "run", "pytest"], check=check)
