"""Scaffolding helpers for creating subclass extension modules."""

from importlib import import_module
from itertools import chain

from InquirerPy import inquirer
from pyrig_runtime.core.dependencies.subclass import DependencySubclass
from pyrig_runtime.core.introspection.classes import discard_abstract_classes

from pyrig.rig.configs.base.copy_module_docstring import (
    CopyModuleDocstringConfigFile,
)


def make_subclass() -> None:
    """Interactively scaffold a subclass module in the current project.

    Prompts the user to select a class, then writes a module file containing
    the selected class's source module docstring and a subclass skeleton that
    imports and extends the chosen class.
    """
    subclass = choose_subclass()

    module_name, class_name = subclass.__module__, subclass.__name__
    module = import_module(module_name)

    config_file = CopyModuleDocstringConfigFile.generate_subclass(module)()
    config_file.validate()
    content = config_file.read_content()

    content += f'''
from {module_name} import {class_name} as Base{class_name}


class {class_name}(Base{class_name}):
    """You can override methods from the base class to customize behavior."""
'''

    config_file.write_content(content)


def choose_subclass() -> type[DependencySubclass]:
    """Present an interactive fuzzy prompt with all available leaf subclasses.

    Returns:
        The class chosen by the user.
    """
    subclass_choices = set(DependencySubclass.subclasses())

    concrete_subclass_choices = set(discard_abstract_classes(subclass_choices))
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
        key=lambda c: c["name"],
    )

    return inquirer.fuzzy(
        message="Select a class to subclass:",
        choices=choices,
    ).execute()
