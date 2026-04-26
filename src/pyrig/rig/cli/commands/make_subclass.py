"""Scaffolding helpers for creating subclass extension modules."""

from importlib import import_module

from InquirerPy import inquirer

from pyrig.core.dependency_subclass import DependencySubclass
from pyrig.core.introspection.classes import (
    discard_abstract_classes,
)
from pyrig.core.introspection.modules import callable_obj_import_path
from pyrig.core.iterate import combine_generators
from pyrig.rig.configs.base.copy_module_docstring import CopyModuleDocstringConfigFile
from pyrig.rig.utils.dependency_subclass import RigDependencySubclass


def make_subclass() -> None:
    """Interactively scaffold a subclass module for a selected pyrig class.

    Prompts the user to pick a class from all discovered ``RigDependencySubclass``
    subclasses, then creates (or validates) the corresponding module file in the
    current project. The file is populated with the source module's docstring and
    a ready-to-use subclass skeleton that imports and extends the chosen class.
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
    """Present an interactive fuzzy prompt and return the chosen class.

    Discovers all concrete and abstract ``RigDependencySubclass`` subclasses,
    formats them for display (concrete classes use their string representation,
    abstract classes use their qualified name), sorts them alphabetically by
    import path, and delegates selection to an InquirerPy fuzzy prompt.

    Returns:
        The class chosen by the user.
    """
    subclass_choices = set(RigDependencySubclass.subclasses())

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
            "name": f"{cls.__module__}.{cls.__name__}",
            "value": cls,
        }
        for cls in abstract_subclass_choices
    )

    choices = sorted(
        combine_generators(concrete_choices, abstract_choices),
        key=lambda c: callable_obj_import_path(c["value"]),
    )

    return inquirer.fuzzy(
        message="Select a class to subclass:",
        choices=choices,
    ).execute()
