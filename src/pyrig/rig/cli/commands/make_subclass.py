"""Helpers to scaffold subclass extension modules for pyrig classes."""

from importlib import import_module

from InquirerPy import inquirer

from pyrig.core.dependency_subclass import DependencySubclass
from pyrig.core.introspection.classes import (
    discard_abstract_classes,
)
from pyrig.core.introspection.modules import callable_obj_import_path
from pyrig.core.iterate import combine_generators
from pyrig.rig.configs.base.copy_module_docstr import CopyModuleOnlyDocstringConfigFile
from pyrig.rig.utils.dependency_subclass import RigDependencySubclass


def make_subclass() -> None:
    """Create a subclass scaffold module for a selected class.

    If `import_path` is not provided, an interactive fuzzy prompt is shown to
    select a discoverable class from pyrig dependents. The target module file is
    created (or validated) via config generation and then extended with a
    subclass skeleton.

    Args:
        import_path: Dotted import path to the class to subclass
            (for example: ``package.module.ClassName``). If ``None``, the class
            is selected interactively.
    """
    subclass = choose_subclass()

    module_name, class_name = subclass.__module__, subclass.__name__
    module = import_module(module_name)

    config_file = CopyModuleOnlyDocstringConfigFile.generate_subclass(module)()
    config_file.validate()

    content = config_file.file_content()

    content += f'''
from {module_name} import {class_name} as Base{class_name}


class {class_name}(Base{class_name}):
    """You can override methods from the base class to customize behavior."""
'''
    config_file.dump(config_file.split_lines(content))


def choose_subclass() -> type[DependencySubclass]:
    """Interactively select a class and return its dotted import path.

    Returns:
        Dotted import path in the form ``module.ClassName`` for the selected
        subclass target.
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
