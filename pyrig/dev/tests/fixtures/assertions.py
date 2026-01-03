"""Assertion fixtures for test coverage and code completeness verification.

Provides fixtures that enforce test coverage by verifying all source code has
corresponding tests. Missing tests are automatically detected and test skeletons
are generated.
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
from pyrig.src.processes import run_subprocess

logger = logging.getLogger(__name__)


@pytest.fixture
def main_test_fixture(mocker: MockerFixture) -> None:
    """Verify that the main entry point is properly configured and callable.

    Tests that the main module is callable via CLI and that ``main()`` is
    invoked exactly once. Also runs the main module as ``__main__`` to
    ensure pytest-cov captures coverage.

    Args:
        mocker: pytest-mock fixture for mocking the main() function.

    Raises:
        AssertionError: If main is not callable via CLI or main() is not
            called exactly once.
    """
    project_name = PyprojectConfigFile.get_project_name()
    src_package_name = PyprojectConfigFile.get_package_name()

    cmds = [
        PackageManager.L.get_run_args(project_name, "--help"),
        PackageManager.L.get_run_args(project_name, main.main.__name__, "--help"),
    ]
    success = False
    for cmd in cmds:
        completed_process = run_subprocess(cmd, check=False)
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

    lines = MainConfigFile.get_lines()
    config_main_module_content = MainConfigFile.make_string_from_lines(lines)

    if main_module_content == config_main_module_content:
        runpy.run_module(main_module_name, run_name="__main__")
