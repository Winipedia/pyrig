"""CLI command module for generating test skeletons across the project."""

from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def make_tests() -> None:
    """Generate test skeletons for all untested source code.

    Resolves the active leaf subclass of ``MirrorTestConfigFile`` (a
    project-specific subclass if one exists, otherwise the base class itself),
    then calls ``validate_all_subclasses``.  That method iterates every module
    in the project's source package, creates a dynamic
    ``MirrorTestConfigFile`` subclass for each one, and validates it—writing
    or updating the corresponding test file with ``NotImplementedError`` stubs
    for any functions, classes, or methods that do not yet have tests.

    The operation is non-destructive: existing test implementations are never
    overwritten.
    """
    MirrorTestConfigFile.L.validate_all_subclasses()
