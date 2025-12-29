"""Assertion fixtures for test coverage and code completeness verification.

Provides fixtures that enforce test coverage by verifying all source code has
corresponding tests. Missing tests are automatically detected and test skeletons
are generated.

Fixtures:
    assert_no_untested_objs: Session-scoped callable that verifies all objects
        in a module/class have corresponding tests, auto-generating skeletons
        for missing tests.
    main_test_fixture: Function-scoped fixture for verifying main entry point
        is callable via CLI.
"""

import logging
import runpy
import sys
from collections.abc import Callable
from importlib import import_module
from types import ModuleType
from typing import Any

import pytest
from pytest_mock import MockerFixture

from pyrig import main
from pyrig.dev.cli.commands.create_tests import create_test_module
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.configs.python.main import MainConfigFile
from pyrig.dev.utils.testing import session_fixture
from pyrig.src.management.package_manager import PackageManager
from pyrig.src.modules.inspection import get_module_of_obj
from pyrig.src.modules.module import (
    get_module_content_as_str,
    get_module_name_replacing_start_module,
    make_obj_importpath,
)
from pyrig.src.modules.package import get_objs_from_obj
from pyrig.src.os.os import run_subprocess
from pyrig.src.testing.convention import (
    get_obj_from_test_obj,
    make_summary_error_msg,
    make_test_obj_importpath_from_obj,
)

logger = logging.getLogger(__name__)


@session_fixture
def assert_no_untested_objs() -> Callable[
    [ModuleType | type | Callable[..., Any]], None
]:
    """Provide a callable that verifies all objects have corresponding tests.

    Returns a session-scoped callable that checks if every function, class, or
    method in a source object has a corresponding test. Automatically generates
    test skeletons for missing tests before failing.

    Returns:
        Callable that takes a test object (module, class, or function) and
        asserts all corresponding source objects have tests.
        Signature: ``(test_obj: ModuleType | type | Callable[..., Any]) -> None``

    Note:
        Skips silently if the source module doesn't exist (custom test module).
    """

    def _assert_no_untested_objs(
        test_obj: ModuleType | type | Callable[..., Any],
    ) -> None:
        """Assert that all objects in the source have corresponding test objects.

        This function verifies that every object (function, class, or method) in the
        source module or class has a corresponding test object
        in the test module or class.

        Args:
            test_obj: The test object (module, class, or function) to check

        Raises:
            AssertionError: If any object lacks a corresponding test object,
                with a detailed error message listing the untested objects

        """
        test_objs = get_objs_from_obj(test_obj)
        test_objs_paths = {make_obj_importpath(obj) for obj in test_objs}

        try:
            obj = get_obj_from_test_obj(test_obj)
        except ImportError:
            if isinstance(test_obj, ModuleType):
                # we skip if module not found bc that means it has custom tests
                # and is not part of the mirrored structure
                logger.debug("No source module found for %s, skipping", test_obj)
                return
            raise
        objs = get_objs_from_obj(obj)
        test_obj_path_to_obj = {
            make_test_obj_importpath_from_obj(obj): obj for obj in objs
        }

        missing_test_obj_path_to_obj = {
            test_path: obj
            for test_path, obj in test_obj_path_to_obj.items()
            if test_path not in test_objs_paths
        }

        # get the modules of these obj
        if missing_test_obj_path_to_obj:
            module = get_module_of_obj(obj)
            create_test_module(module)

        msg = f"""Found missing tests. Tests skeletons were automatically created for:
        {make_summary_error_msg(missing_test_obj_path_to_obj.keys())}
    """

        assert not missing_test_obj_path_to_obj, msg

    return _assert_no_untested_objs


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
        PackageManager.get_run_args(project_name, "--help"),
        PackageManager.get_run_args(project_name, main.main.__name__, "--help"),
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
    config_main_module_content = MainConfigFile.get_content_str()

    if main_module_content == config_main_module_content:
        runpy.run_module(main_module_name, run_name="__main__")
