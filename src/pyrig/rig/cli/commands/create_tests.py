"""Automatic test skeleton generation for source code.

Generates test files mirroring the source package structure, creating skeleton
test functions and classes with `NotImplementedError` placeholders for all
untested code.
"""

from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def create_tests() -> None:
    """Generate test skeletons for all source code.

    Delegates to `MirrorTestConfigFile.I.create_all_test_modules`, which
    retrieves all modules from the projects source package and creates test
    files for them.
    """
    MirrorTestConfigFile.I.create_all_test_modules()
