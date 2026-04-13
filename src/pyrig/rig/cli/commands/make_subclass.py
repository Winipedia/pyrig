"""Helpers to scaffold subclass extension modules for pyrig classes."""

from importlib import import_module

from InquirerPy import inquirer

import pyrig
from pyrig import rig
from pyrig.core.dependency_subclass import DependencySubclass
from pyrig.core.modules.class_ import discard_parent_classes
from pyrig.core.modules.package import discover_subclasses_across_dependents
from pyrig.rig.configs.base.copy_module_docstr import CopyModuleOnlyDocstringConfigFile


def make_subclass(import_path: str | None) -> None:
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
    if import_path is None:
        import_path = choose_subclass()

    module_name, class_name = import_path.rsplit(".", 1)
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


def choose_subclass() -> str:
    """Interactively select a class and return its dotted import path.

    Returns:
        Dotted import path in the form ``module.ClassName`` for the selected
        subclass target.
    """
    subclass_choices = discard_parent_classes(
        discover_subclasses_across_dependents(
            DependencySubclass,
            dep=pyrig,
            load_package_before=rig,
        )
    )

    choices = [
        {
            "name": f"{cls_name} ({module_name})",
            "value": f"{module_name}.{cls_name}",
        }
        for cls_name, module_name in (
            (cls.__name__, cls.__module__) for cls in subclass_choices
        )
    ]

    return inquirer.fuzzy(
        message="Select a class to subclass:",
        choices=choices,
    ).execute()
