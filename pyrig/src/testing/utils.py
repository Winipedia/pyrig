"""Testing utilities for introspection and validation.

This module provides utility functions for working with tests, including:
- Asserting that all objects in the source have corresponding test objects
- Generating the content for a conftest.py file

Returns:
    Various utility functions for testing introspection and validation.

"""

import logging
from collections.abc import Callable
from types import ModuleType
from typing import Any

from pyrig.src.modules.module import (
    get_objs_from_obj,
    make_obj_importpath,
)
from pyrig.src.testing.assertions import assert_with_msg
from pyrig.src.testing.convention import (
    get_obj_from_test_obj,
    make_test_obj_importpath_from_obj,
    make_untested_summary_error_msg,
)
from pyrig.src.testing.create_tests import create_tests

logger = logging.getLogger(__name__)


def assert_no_untested_objs(
    test_obj: ModuleType | type | Callable[..., Any],
) -> None:
    """Assert that all objects in the source have corresponding test objects.

    This function verifies that every object (function, class, or method) in the
    source module or class has a corresponding test object in the test module or class.

    Args:
        test_obj: The test object (module, class, or function) to check

    Raises:
        AssertionError: If any object in the source lacks a corresponding test object,
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
    test_obj_path_to_obj = {make_test_obj_importpath_from_obj(obj): obj for obj in objs}

    missing_test_obj_path_to_obj = {
        test_path: obj
        for test_path, obj in test_obj_path_to_obj.items()
        if test_path not in test_objs_paths
    }

    # get the modules of these obj
    if missing_test_obj_path_to_obj:
        create_tests()

    msg = f"""Found missing tests. Tests skeletons were automatically created for:
    {make_untested_summary_error_msg(missing_test_obj_path_to_obj.keys())}
"""

    assert_with_msg(
        not missing_test_obj_path_to_obj,
        msg,
    )
