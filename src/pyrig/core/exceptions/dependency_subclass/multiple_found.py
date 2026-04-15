"""Exception raised when multiple subclasses are found for a DependencySubclass."""

import json
from typing import TYPE_CHECKING

from pyrig.core.exceptions.base.dependency_subclass import DependencySubclassError
from pyrig.core.introspection.packages import all_deps_depending_on_dep

if TYPE_CHECKING:
    from pyrig.core.dependency_subclass import DependencySubclass


class MultipleSubclassesFoundError(DependencySubclassError):
    """Raised when multiple subclasses are found for a given DependencySubclass."""

    def __init__(self, subcls: type["DependencySubclass"]) -> None:
        """Initialize the error with the given subclass type."""
        cls_name = subcls.__name__
        subclasses = subcls.subclasses()
        subclass_names = json.dumps([str(subcls) for subcls in subclasses], indent=4)
        pyrig_dependecies = ", ".join(
            dep.__name__ for dep in all_deps_depending_on_dep(subcls.base_dependency())
        )
        msg = f"""Multiple subclasses found for {cls_name}.
Defining multiple leaf subclasses for {cls_name} is ambiguous.
This can happen if more than one leaf subclass of {cls_name} is defined
across the dependent packages: {pyrig_dependecies}.

{self.command_recommendation()}

Found subclasses:
{subclass_names}
"""
        super().__init__(msg)
