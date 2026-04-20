"""Automatic test skeleton generation for source code.

Generates test files mirroring the source package structure, creating skeleton
test functions and classes with `NotImplementedError` placeholders for all
untested code.
"""

from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def make_tests() -> None:
    """Generate test skeletons for all source code.

    Delegates to `MirrorTestConfigFile.L.validate_all_subclasses`, which
    retrieves all subclasses and validates their implementation.
    """
    MirrorTestConfigFile.L.validate_all_subclasses()
