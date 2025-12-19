"""Fixtures that assert some state or condition."""

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
from pyrig.dev.cli.commands.create_tests import make_test_skeletons
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.configs.python.main import MainConfigFile
from pyrig.dev.utils.testing import session_fixture
from pyrig.src.modules.module import (
    get_module_content_as_str,
    get_module_name_replacing_start_module,
    make_obj_importpath,
)
from pyrig.src.modules.package import get_objs_from_obj
from pyrig.src.os.os import run_subprocess
from pyrig.src.project.mgt import DependencyManager
from pyrig.src.testing.assertions import assert_with_msg
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
    """Fixture that asserts that all objects of an object have corresponding tests.

    This fixture provides a function that can be called to assert that all objects
    (functions, classes, or methods) in a given module, class, or function have
    corresponding test objects in the test module, class, or function.

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
                logger.warning("No source module found for %s, skipping", test_obj)
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
            make_test_skeletons()

        msg = f"""Found missing tests. Tests skeletons were automatically created for:
        {make_summary_error_msg(missing_test_obj_path_to_obj.keys())}
    """

        assert_with_msg(
            not missing_test_obj_path_to_obj,
            msg,
        )

    return _assert_no_untested_objs


@pytest.fixture
def main_test_fixture(mocker: MockerFixture) -> None:
    """Fixture for testing main."""
    project_name = PyprojectConfigFile.get_project_name()
    src_package_name = PyprojectConfigFile.get_package_name()

    cmds = [
        DependencyManager.get_run_args(project_name, main.main.__name__),
        DependencyManager.get_run_args(project_name, main.main.__name__, "--help"),
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

    main_module_name = get_module_name_replacing_start_module(main, src_package_name)
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
