"""Automatic test skeleton generation for source code.

Generates test files mirroring the source package structure, creating skeleton
test functions and classes with NotImplementedError placeholders for all
untested code.
"""

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from types import ModuleType

from pyrig.dev.utils.packages import get_src_package
from pyrig.src.modules.class_ import (
    get_all_cls_from_module,
    get_all_methods_from_cls,
)
from pyrig.src.modules.function import get_all_functions_from_module
from pyrig.src.modules.imports import walk_package
from pyrig.src.modules.inspection import get_qualname_of_obj
from pyrig.src.modules.module import (
    create_module,
    get_isolated_obj_name,
    get_module_content_as_str,
)
from pyrig.src.modules.package import create_package
from pyrig.src.modules.path import ModulePath
from pyrig.src.testing.convention import (
    get_test_obj_from_obj,
    make_test_obj_importpath_from_obj,
    make_test_obj_name,
)

logger = logging.getLogger(__name__)


def make_test_skeletons() -> None:
    """Create test skeleton files for all source code.

    Walks the source package hierarchy and creates corresponding test packages,
    modules, classes, and functions for all untested code.
    """
    logger.info("Creating test skeletons")
    src_package = get_src_package()
    logger.debug("Source package: %s", src_package.__name__)
    create_tests_for_package(src_package)
    logger.info("Test skeleton creation complete")


def create_tests_for_package(package: ModuleType) -> None:
    """Create test files for all modules in a source package.

    Walks the package hierarchy and creates corresponding test packages and
    modules using parallel execution.

    Args:
        package: The source package to create tests for.
    """
    logger.debug("Creating tests for package: %s", package.__name__)
    futures: list[Future[None]] = []
    with ThreadPoolExecutor() as executor:
        for pkg, modules in walk_package(package):
            if not modules:
                futures.append(executor.submit(create_test_package, pkg))
            futures.extend(
                executor.submit(create_test_module, module) for module in modules
            )
    for future in futures:
        # call result so errors raise
        future.result()


def create_test_package(package: ModuleType) -> None:
    """Create a test package for a source package.

    Args:
        package: The source package to create a test package for.
    """
    test_package_name = make_test_obj_importpath_from_obj(package)
    test_package_path = ModulePath.pkg_name_to_relative_dir_path(test_package_name)
    # create package if it doesn't exist
    create_package(test_package_path)


def create_test_module(module: ModuleType) -> None:
    """Create a test module for a source module.

    Generates test module content with skeleton test functions and classes,
    then writes it to the test module file.

    Args:
        module: The source module to create a test module for.
    """
    test_module_name = make_test_obj_importpath_from_obj(module)
    test_module_path = ModulePath.module_name_to_relative_file_path(test_module_name)

    test_module = create_module(test_module_path)
    test_module_path = ModulePath.module_type_to_file_path(test_module)

    test_module_path.write_text(get_test_module_content(module))


def get_test_module_content(module: ModuleType) -> str:
    """Generate test module content for a source module.

    Combines existing test content with new test functions and classes for
    untested code.

    Args:
        module: The source module to generate test content for.

    Returns:
        The complete test module content as a string.
    """
    test_module = get_test_obj_from_obj(module)
    test_module_content = get_module_content_as_str(test_module)

    test_module_content = get_test_functions_content(
        module, test_module, test_module_content
    )

    return get_test_classes_content(module, test_module, test_module_content)


def get_test_functions_content(
    module: ModuleType,
    test_module: ModuleType,
    test_module_content: str,
) -> str:
    """Generate test function skeletons for untested functions.

    Args:
        module: The source module containing functions to test.
        test_module: The test module to add function tests to.
        test_module_content: The current content of the test module.

    Returns:
        Updated test module content with new test function skeletons.
    """
    funcs = get_all_functions_from_module(module)
    test_functions = get_all_functions_from_module(test_module)
    supposed_test_funcs_names = [make_test_obj_name(f) for f in funcs]

    test_funcs_names = [get_qualname_of_obj(f) for f in test_functions]

    untested_funcs_names = [
        f for f in supposed_test_funcs_names if f not in test_funcs_names
    ]

    for test_func_name in untested_funcs_names:
        test_module_content += f'''

def {test_func_name}() -> None:
    """Test function."""
    raise {NotImplementedError.__name__}
'''

    return test_module_content


def get_test_classes_content(
    module: ModuleType,
    test_module: ModuleType,
    test_module_content: str,
) -> str:
    """Generate test class skeletons for untested classes and methods.

    Identifies untested classes and methods, generates skeleton test classes
    and methods, and inserts them into the test module content.

    Args:
        module: The source module containing classes to test.
        test_module: The test module to add class tests to.
        test_module_content: The current content of the test module.

    Returns:
        Updated test module content with new test class skeletons.

    Raises:
        ValueError: If a test class declaration appears multiple times in the
            test module.
    """
    classes = get_all_cls_from_module(module)
    test_classes = get_all_cls_from_module(test_module)

    class_to_methods = {
        c: get_all_methods_from_cls(c, exclude_parent_methods=True) for c in classes
    }
    test_class_to_methods = {
        tc: get_all_methods_from_cls(tc, exclude_parent_methods=True)
        for tc in test_classes
    }

    supposed_test_class_to_methods_names = {
        make_test_obj_name(c): [make_test_obj_name(m) for m in ms]
        for c, ms in class_to_methods.items()
    }
    test_class_to_methods_names = {
        get_isolated_obj_name(tc): [get_isolated_obj_name(tm) for tm in tms]
        for tc, tms in test_class_to_methods.items()
    }

    untested_test_class_to_methods_names: dict[str, list[str]] = {}
    for (
        test_class_name,
        supposed_test_methods_names,
    ) in supposed_test_class_to_methods_names.items():
        test_methods_names = test_class_to_methods_names.get(test_class_name, [])
        untested_methods_names = [
            tmn for tmn in supposed_test_methods_names if tmn not in test_methods_names
        ]
        if (
            not supposed_test_methods_names
            and test_class_name not in test_class_to_methods_names
        ):
            untested_test_class_to_methods_names[test_class_name] = []
        if untested_methods_names:
            untested_test_class_to_methods_names[test_class_name] = (
                untested_methods_names
            )

    for (
        test_class_name,
        untested_methods_names,
    ) in untested_test_class_to_methods_names.items():
        test_class_declaration = f'''
class {test_class_name}:
    """Test class."""
'''
        test_class_content = test_class_declaration
        for untested_method_name in untested_methods_names:
            test_class_content += f'''
    def {untested_method_name}(self) -> None:
        """Test method."""
        raise {NotImplementedError.__name__}
'''
        parts = test_module_content.split(test_class_declaration)
        expected_parts = 2
        if len(parts) > expected_parts:
            msg = f"Found {len(parts)} parts, expected 2"
            raise ValueError(msg)
        parts.insert(1, test_class_content)
        test_module_content = "".join(parts)

    return test_module_content
