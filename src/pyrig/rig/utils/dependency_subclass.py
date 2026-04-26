"""Rig-layer intermediate base class for cross-package subclass discovery."""

from types import ModuleType

import pyrig
from pyrig import rig
from pyrig.core.dependency_subclass import DependencySubclass


class RigDependencySubclass(DependencySubclass):
    """Shared base class for all rig subsystem classes.

    Pre-configures the two abstract hooks required by ``DependencySubclass``
    so that tools, config files, builders, and other rig subsystem classes
    gain automatic cross-package subclass discovery without additional
    boilerplate.

    Discovery is scoped to the ``pyrig.rig`` namespace (``definition_package``)
    and spans every installed package that declares ``pyrig`` as a dependency
    (``base_dependency``). Any new rig subsystem class should inherit from
    this class, or from an intermediate such as ``Tool`` or ``ConfigFile``,
    rather than from ``DependencySubclass`` directly.
    """

    @classmethod
    def definition_package(cls) -> ModuleType:
        """Return ``pyrig.rig`` as the namespace for subclass discovery.

        Scopes cross-package discovery to the rig layer so that only rig
        subsystem implementations are found when searching dependent packages.
        Subclasses are encouraged to be defined a sub-package of ``pyrig.rig``
        to keep the discovery process organized.

        Returns:
            The ``pyrig.rig`` module.
        """
        return rig

    @classmethod
    def base_dependency(cls) -> ModuleType:
        """Return ``pyrig`` as the root package for dependent-package discovery.

        The discovery engine searches every installed package that declares
        ``pyrig`` as a dependency when looking for subclasses.

        Returns:
            The ``pyrig`` package module.
        """
        return pyrig
