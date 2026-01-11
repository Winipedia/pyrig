"""Assertion fixtures for verifying project entry point configuration.

Provides pytest fixtures that verify the main entry point is correctly configured
and callable. Used by pyrig-based projects to validate their CLI setup in tests.

See Also:
    pyrig.dev.configs.python.main.MainConfigFile: Generates main.py template.
    pyrig.dev.tests.conftest: Automatic fixture discovery and registration.
"""

import logging
import runpy
import sys
from importlib import import_module

import pytest
from pytest_mock import MockerFixture

from pyrig import main
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.configs.python.main import MainConfigFile
from pyrig.dev.management.package_manager import PackageManager
from pyrig.src.modules.module import (
    get_module_content_as_str,
    get_module_name_replacing_start_module,
)

logger = logging.getLogger(__name__)


@pytest.fixture
def main_test_fixture(mocker: MockerFixture) -> None:
    """Fixture that verifies the project's main entry point configuration.

    Validates that:
        1. The CLI entry point is callable via ``uv run <project>`` commands
        2. The ``main()`` function is invoked exactly once when called
        3. Coverage is captured when running as ``__main__`` (only if main.py
           content matches pyrig's template)

    Intended for use in test_main.py of pyrig-based projects::

        def test_main(main_test_fixture: None) -> None:
            pass

    Args:
        mocker: pytest-mock fixture for mocking ``main()``.

    Raises:
        AssertionError: If CLI is not callable or ``main()`` call count != 1.

    See Also:
        pyrig.dev.configs.testing.main_test.MainTestConfigFile: Generates test.
        pyrig.dev.configs.python.main.MainConfigFile: Generates main.py.
    """
    project_name = PyprojectConfigFile.L.get_project_name()
    src_package_name = PyprojectConfigFile.L.get_package_name()

    cmds = [
        PackageManager.L.get_run_args(project_name, "--help"),
        PackageManager.L.get_run_args(project_name, main.main.__name__, "--help"),
    ]
    success = False
    for cmd in cmds:
        completed_process = cmd.run(check=False)
        if completed_process.returncode == 0:
            success = True
            break
    else:
        cmd_strs = [" ".join(cmd) for cmd in cmds]
        msg = f"Expected {main.main.__name__} to be callable by one of {cmd_strs}"
        assert success, msg

    main_module_name = get_module_name_replacing_start_module(main, src_package_name)
    main_module = import_module(main_module_name)
    main_mock = mocker.patch.object(main_module, main.main.__name__)
    main_module.main()
    assert main_mock.call_count == 1, (
        f"Expected main to be called, got {main_mock.call_count} calls"
    )

    # must run main module directly as __main__
    # so that pytest-cov sees that it calls main
    # remove module if already imported, so run_module reloads it
    del sys.modules[main_module_name]
    # run module as __main__, pytest-cov will see it
    # run only if file content is the same as pyrig.main
    main_module_content = get_module_content_as_str(main_module)

    lines = MainConfigFile.L.get_lines()
    config_main_module_content = MainConfigFile.L.make_string_from_lines(lines)

    if main_module_content == config_main_module_content:
        runpy.run_module(main_module_name, run_name="__main__")
