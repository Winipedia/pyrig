"""Exception raised when no subclasses are found for a DependencySubclass."""

from typing import TYPE_CHECKING

from pyrig.core.exceptions.base.dependency_subclass import DependencySubclassError

if TYPE_CHECKING:
    from pyrig.core.dependency_subclass import DependencySubclass


class NoSubclassesFoundError(DependencySubclassError):
    """Raised when no subclasses are found for a given DependencySubclass."""

    def __init__(self, cls: type["DependencySubclass"]) -> None:
        """Initialize the error with the given subclass type."""
        cls_name = cls.__name__
        definition_package_name = cls.definition_package().__name__
        message = f"""No subclasses found for {cls_name}.
Subclasses must be concrete and implement all abstract methods.
They also must be defined under the same relative definition package.
E.g.: if {cls_name} is defined in a submodule of {definition_package_name},
then subclasses must be defined in a submodule of {definition_package_name}
within the same or a dependent package.

{self.command_recommendation()}
"""
        super().__init__(message)
