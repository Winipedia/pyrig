"""Scaffolding helpers for creating subclass extension modules."""

from importlib import import_module
from itertools import chain
from operator import itemgetter

from InquirerPy import inquirer
from pyrig_runtime.core.dependencies.subclass import DependencySubclass
from pyrig_runtime.core.introspection.classes import filter_concrete_classes

from pyrig.rig.configs.base.copy_module import (
    CopyModuleDocstringConfigFile,
)


def make_subclass(reference: tuple[str, str] | None) -> None:
    """Scaffold a subclass module in the current project for the chosen class.

    Resolves the class to subclass either from `reference` or, if `None`, by
    prompting the user to select one interactively. Then writes a module file
    containing the selected class's source module docstring and a subclass
    skeleton that imports and extends the chosen class.

    Args:
        reference: A `(module_name, class_name)` pair identifying the class to
            subclass, or `None` to choose one interactively.
    """
    if reference is None:
        subclass = choose_subclass()
        module_name, class_name = subclass.__module__, subclass.__name__
    else:
        module_name, class_name = reference

    config_file = CopyModuleDocstringConfigFile.generate_subclass(
        import_module(module_name),
    )()
    config_file.validate()
    content = config_file.read_content()

    content += f'''
from {module_name} import {class_name} as Base{class_name}


class {class_name}(Base{class_name}):
    """You can override methods from the base class to customize behavior."""
'''

    config_file.write_content(content)


def choose_subclass() -> type[DependencySubclass]:
    """Present an interactive fuzzy prompt over every `DependencySubclass` subclass.

    Includes both concrete and abstract classes. Concrete classes are labeled
    with their instantiated string representation; abstract classes, which
    cannot be instantiated, use their class string representation instead.

    Returns:
        The class chosen by the user.
    """
    subclass_choices = set(DependencySubclass.subclasses())

    concrete_subclass_choices = set(filter_concrete_classes(subclass_choices))
    abstract_subclass_choices = subclass_choices - concrete_subclass_choices

    concrete_choices = (
        {
            "name": str(cls()),
            "value": cls,
        }
        for cls in concrete_subclass_choices
    )

    abstract_choices = (
        {
            "name": str(cls),
            "value": cls,
        }
        for cls in abstract_subclass_choices
    )

    choices = sorted(
        chain(concrete_choices, abstract_choices),
        key=itemgetter("name"),
    )

    return inquirer.fuzzy(
        message="Select a class to subclass:",
        choices=choices,
    ).execute()
