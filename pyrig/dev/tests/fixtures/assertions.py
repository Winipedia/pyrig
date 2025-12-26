"""Assertion fixtures for test coverage and code completeness verification.

This module provides pytest fixtures that assert various conditions about test
coverage and code structure. These fixtures are automatically registered via
pytest_plugins and are available in all test modules without explicit imports.

The primary fixture, `assert_no_untested_objs`, enforces 100% test coverage by
verifying that every function, class, and method in the source code has a
corresponding test. When untested code is found, the fixture automatically
generates test skeletons and fails with a detailed error message.

Fixtures:
    assert_no_untested_objs: Session-scoped fixture that returns a callable for
        verifying all objects in a module, class, or function have corresponding
        tests. Automatically creates test skeletons for missing tests.

    main_test_fixture: Function-scoped fixture for testing the main entry point.
        Verifies that the main module is callable via CLI and that the main()
        function is properly invoked.

Automatic Test Skeleton Generation:
    When `assert_no_untested_objs` finds untested code, it automatically:
    1. Identifies all missing test functions/classes/methods
    2. Calls `create_test_module()` to generate test skeletons
    3. Fails the test with a detailed error message listing what was created
    4. Allows the developer to fill in the generated test skeletons

This ensures that test coverage never decreases and that new code always has
corresponding test structure, even if the tests are initially empty.

Module Attributes:
    logger (logging.Logger): Logger instance for this module.

See Also:
    pyrig.dev.cli.commands.create_tests.create_test_module: Test skeleton generator
    pyrig.src.testing.convention.get_obj_from_test_obj: Maps test objects to source
    pyrig.src.testing.convention.make_test_obj_importpath_from_obj: Generates test paths
    pyrig.src.modules.package.get_objs_from_obj: Extracts objects from modules/classes
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
    """Provide a callable that verifies all objects have corresponding tests.

    This session-scoped fixture returns a function that can be called to verify
    that every object (function, class, or method) in a given module, class, or
    function has a corresponding test object in the test module, class, or function.

    The fixture enforces 100% test coverage by:
    1. Extracting all objects from the test object (module/class/function)
    2. Finding the corresponding source object via naming convention
    3. Extracting all objects from the source object
    4. Comparing source objects to test objects
    5. Automatically generating test skeletons for missing tests
    6. Failing with a detailed error message if any tests are missing

    Returns:
        A callable that takes a test object (module, class, or function) and
        asserts that all objects in the corresponding source object have tests.
        The callable signature is:
        `(test_obj: ModuleType | type | Callable[..., Any]) -> None`

    Example:
        Using in a test module::

            def test_all_functions_tested(assert_no_untested_objs):
                '''Verify all functions in this module have tests.'''
                import tests.test_mymodule
                assert_no_untested_objs(tests.test_mymodule)

        Using in autouse fixtures (common pattern)::

            @pytest.fixture(autouse=True, scope="module")
            def verify_coverage(request, assert_no_untested_objs):
                '''Automatically verify coverage for this module.'''
                assert_no_untested_objs(request.module)

    Note:
        - This fixture is session-scoped, so it's created once per test session
        - The returned callable can be called multiple times
        - Test skeletons are automatically generated for missing tests
        - If the source module doesn't exist (custom test module), it's skipped

    See Also:
        pyrig.dev.tests.fixtures.autouse.module.assert_all_funcs_and_classes_tested:
            Autouse fixture that calls this for every test module
        pyrig.dev.tests.fixtures.autouse.class_.assert_all_methods_tested:
            Autouse fixture that calls this for every test class
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

        assert_with_msg(
            not missing_test_obj_path_to_obj,
            msg,
        )

    return _assert_no_untested_objs


@pytest.fixture
def main_test_fixture(mocker: MockerFixture) -> None:
    """Verify that the main entry point is properly configured and callable.

    This function-scoped fixture performs comprehensive testing of the main
    entry point to ensure it's properly configured and callable via CLI. It
    verifies that:

    1. The main module is callable via CLI (either as `project-name` or
       `project-name main`)
    2. The main() function is properly invoked when the module is called
    3. The main module can be run as `__main__` for pytest-cov coverage

    The fixture uses pytest-mock to verify that main() is called exactly once
    when the module is invoked. It also runs the main module as `__main__` to
    ensure pytest-cov sees the coverage.

    Args:
        mocker: pytest-mock fixture for mocking the main() function.

    Raises:
        AssertionError: If the main module is not callable via CLI, if main()
            is not called exactly once, or if any other verification fails.

    Example:
        Using in a test::

            def test_main(main_test_fixture):
                '''Test that main entry point works.'''
                # Fixture automatically verifies main is callable
                pass

    Note:
        - This fixture modifies sys.modules to reload the main module
        - It only runs the main module as `__main__` if the content matches
          the expected template from MainConfigFile
        - The fixture verifies both CLI invocation and direct module execution

    See Also:
        pyrig.dev.configs.python.main.MainConfigFile: Expected main module template
        pyrig.src.management.package_manager.PackageManager: CLI command builder
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
