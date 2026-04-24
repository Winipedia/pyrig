"""Contains a dependency subclass for rig classes.

This is used to discover subclasses of rig classes across dependent packages.
"""

from types import ModuleType

import pyrig
from pyrig import rig
from pyrig.core.dependency_subclass import DependencySubclass


class RigDependencySubclass(DependencySubclass):
    """Base class for rig dependency subclasses.

    Implements the base dependency and definition package for rig classes,
    so that subclasses can be discovered across dependent packages
    without additional configuration.
    """

    @classmethod
    def definition_package(cls) -> ModuleType:
        """Return the definition package for this subclass."""
        return rig

    @classmethod
    def base_dependency(cls) -> ModuleType:
        """Return the base dependency module for this subclass."""
        return pyrig
