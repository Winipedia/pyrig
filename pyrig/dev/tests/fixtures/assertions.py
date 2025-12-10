"""Fixtures that assert some state or condition."""

import runpy
import sys
from importlib import import_module

import pytest
from pytest_mock import MockerFixture

from pyrig import main
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.configs.python.main import MainConfigFile
from pyrig.src.modules.module import get_module_content_as_str
from pyrig.src.os.os import run_subprocess
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def main_test_fixture(mocker: MockerFixture) -> None:
    """Fixture for testing main."""
    project_name = PyprojectConfigFile.get_project_name()
    src_package_name = PyprojectConfigFile.get_package_name()

    cmds = [
        ["uv", "run", project_name, "--help"],
        ["uv", "run", project_name, main.main.__name__, "--help"],
    ]
    success = False
    for cmd in cmds:
        completed_process = run_subprocess(cmd, check=False)
        if completed_process.returncode == 0:
            success = True
            break
    else:
        cmd_strs = [" ".join(cmd) for cmd in cmds]
        assert_with_msg(
            success,
            f"Expected {main.main.__name__} to be callable by one of {cmd_strs}",
        )

    main_module_name = PyprojectConfigFile.get_module_name_replacing_start_module(
        main, src_package_name
    )
    main_module = import_module(main_module_name)
    main_mock = mocker.patch.object(main_module, main.main.__name__)
    main_module.main()
    assert_with_msg(
        main_mock.call_count == 1,
        f"Expected main to be called, got {main_mock.call_count}",
    )

    # must run main module directly as __main__
    # so that pytest-cov sees that it calls main
    # remove module if already imported, so run_module reloads it
    del sys.modules[main_module_name]
    # run module as __main__, pytest-cov will see it
    # run only if file content is the same as pyrig.main
    main_module_content = get_module_content_as_str(main_module)
    config_main_module_content = MainConfigFile.get_content_str()

    if main_module_content == config_main_module_content:
        runpy.run_module(main_module_name, run_name="__main__")
