"""Utilities for automatically creating test files for the project.

This module provides functions to generate test files for all modules and classes
in the project, ensuring that every function and method has a corresponding test.
It creates the basic test structure and generates skeleton test functions with
NotImplementedError to indicate tests that need to be written.
"""

from types import ModuleType
from typing import cast

from pyrig.dev import tests
from pyrig.src.modules.class_ import (
    get_all_cls_from_module,
    get_all_methods_from_cls,
)
from pyrig.src.modules.function import get_all_functions_from_module
from pyrig.src.modules.inspection import get_qualname_of_obj
from pyrig.src.modules.module import (
    create_module,
    get_isolated_obj_name,
    get_module_content_as_str,
    to_path,
)
from pyrig.src.modules.package import (
    copy_package,
    get_src_package,
    walk_package,
)
from pyrig.src.testing.convention import (
    TESTS_PACKAGE_NAME,
    get_test_obj_from_obj,
    make_test_obj_importpath_from_obj,
    make_test_obj_name,
)


def create_tests() -> None:
    """Create all test files for the project.

    This function orchestrates the test creation process by first setting up the base
    test structure and then creating test files for all source packages.
    """
    create_tests_base()
    create_tests_for_package(get_src_package())


def create_tests_base() -> None:
    """Create the base test structure.

    This function:
    1. Creates a mirror of testing.tests in the tests directory
    2. Skips copying __init__.py file contents
    3. Writes new __init__.py files for all packages
    4. Creates a conftest.py file with the appropriate pytest plugin configuration
    5. Does not overwrite anything if it already exists except conftest.py
    """
    copy_package(
        src_package=tests,
        dst=TESTS_PACKAGE_NAME,
        with_file_content=False,
    )


def create_tests_for_package(package: ModuleType) -> None:
    """Create test files for all modules in the source package.

    This function walks through the source package hierarchy and creates corresponding
    test packages and modules for each package and module found in the source.
    """
    for pkg, modules in walk_package(package):
        create_test_package(pkg)
        for module in modules:
            create_test_module(module)


def create_test_package(package: ModuleType) -> None:
    """Create a test package for a source package.

    Args:
        package: The source package module to create a test package for

    This function creates a test package with the appropriate naming convention
    if it doesn't already exist.

    """
    test_package_name = make_test_obj_importpath_from_obj(package)
    # create package if it doesn't exist
    create_module(test_package_name, is_package=True)


def create_test_module(module: ModuleType) -> None:
    """Create a test module for a source module.

    Args:
        module: The source module to create a test module for

    This function:
    1. Creates a test module with the appropriate naming convention
    2. Generates the test module content with skeleton test functions
    3. Writes the content to the test module file

    """
    test_module_name = make_test_obj_importpath_from_obj(module)
    test_module = create_module(test_module_name, is_package=False)
    test_module_path = to_path(test_module, is_package=False)
    test_module_path.write_text(get_test_module_content(module))


def get_test_module_content(module: ModuleType) -> str:
    """Generate the content for a test module.

    Args:
        module: The source module to generate test content for

    Returns:
        The generated test module content as a string

    This function:
    1. Gets the existing test module content if it exists
    2. Adds test functions for all functions in the source module
    3. Adds test classes for all classes in the source module

    """
    test_module = cast("ModuleType", (get_test_obj_from_obj(module)))
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
    """Generate test function content for a module.

    Args:
        module: The source module containing functions to test
        test_module: The test module to add function tests to
        test_module_content: The current content of the test module

    Returns:
        The updated test module content with function tests added

    This function:
    1. Identifies all functions in the source module
    2. Determines which functions don't have corresponding tests
    3. Generates skeleton test functions for untested functions

    """
    funcs = get_all_functions_from_module(module)
    test_functions = get_all_functions_from_module(test_module)
    supposed_test_funcs_names = [make_test_obj_name(f) for f in funcs]

    test_funcs_names = [get_qualname_of_obj(f) for f in test_functions]

    untested_funcs_names = [
        f for f in supposed_test_funcs_names if f not in test_funcs_names
    ]

    for test_func_name in untested_funcs_names:
        test_module_content += f"""

def {test_func_name}() -> None:
    \"\"\"Test function.\"\"\"
    raise {NotImplementedError.__name__}
"""

    return test_module_content


def get_test_classes_content(
    module: ModuleType,
    test_module: ModuleType,
    test_module_content: str,
) -> str:
    """Generate test class content for a module.

    Args:
        module: The source module containing classes to test
        test_module: The test module to add class tests to
        test_module_content: The current content of the test module

    Returns:
        The updated test module content with class tests added

    This function:
    1. Identifies all classes in the source module
    2. Determines which classes and methods don't have corresponding tests
    3. Generates skeleton test classes and methods for untested classes and methods
    4. Inserts the new test classes into the existing content
       if the class already exists

    Raises:
        ValueError: If a test class declaration appears multiple
                    times in the test module

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
        test_class_declaration = f"""
class {test_class_name}:
    \"\"\"Test class.\"\"\"
"""
        test_class_content = test_class_declaration
        for untested_method_name in untested_methods_names:
            test_class_content += f"""
    def {untested_method_name}(self) -> None:
        \"\"\"Test method.\"\"\"
        raise {NotImplementedError.__name__}
"""
        parts = test_module_content.split(test_class_declaration)
        expected_parts = 2
        if len(parts) > expected_parts:
            msg = f"Found {len(parts)} parts, expected 2"
            raise ValueError(msg)
        parts.insert(1, test_class_content)
        test_module_content = "".join(parts)

    return test_module_content
