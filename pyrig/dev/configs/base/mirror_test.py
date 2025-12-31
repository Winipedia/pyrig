import importlib
import logging
from abc import abstractmethod
from collections import defaultdict
from pathlib import Path
from types import ModuleType
from typing import Any, Self, cast

from pyrig.dev.configs.base.py_package import PythonPackageConfigFile
from pyrig.src.modules.class_ import get_all_cls_from_module, get_all_methods_from_cls
from pyrig.src.modules.function import get_all_functions_from_module
from pyrig.src.modules.inspection import get_qualname_of_obj
from pyrig.src.modules.module import (
    get_default_module_content,
    get_isolated_obj_name,
    get_module_content_as_str,
    import_module_with_file_fallback,
)
from pyrig.src.modules.path import ModulePath
from pyrig.src.string import make_name_from_obj, starts_with_docstring
from pyrig.src.testing.convention import (
    make_test_obj_importpath_from_obj,
    make_test_obj_name,
)

logger = logging.getLogger(__name__)


class MirrorTestConfigFile(PythonPackageConfigFile):
    @classmethod
    @abstractmethod
    def get_src_module(cls) -> ModuleType:
        """The module or package to mirror and create tests for."""

    @classmethod
    def get_filename(cls) -> str:
        test_path = cls.get_test_path()
        return test_path.stem  # filename without extension

    @classmethod
    def get_parent_path(cls) -> Path:
        test_path = cls.get_test_path()
        return test_path.parent

    @classmethod
    def get_content_str(cls) -> str:
        return cls.get_test_module_content_with_skeletons()

    @classmethod
    def _dump(cls, config: dict[str, Any] | list[Any]) -> None:
        super()._dump(config)
        # need to reload the test module to reflect the new content
        importlib.reload(cls.get_test_module())

    @classmethod
    def override_content(cls) -> bool:
        return True

    @classmethod
    def is_correct(cls) -> bool:
        no_untested_funcs = cls.get_untested_func_names() == []
        no_untested_classes = cls.get_untested_class_and_method_names() == {}
        return super().is_correct() or (no_untested_funcs and no_untested_classes)

    @classmethod
    def get_test_path(cls) -> Path:
        test_module_name = cls.get_test_module_name()
        return ModulePath.module_name_to_relative_file_path(test_module_name)

    @classmethod
    def get_test_module_name(cls) -> str:
        return cls.get_test_module_name_from_src_module(cls.get_src_module())

    @classmethod
    def get_test_module_name_from_src_module(cls, src_module: ModuleType) -> str:
        return make_test_obj_importpath_from_obj(src_module)

    @classmethod
    def get_test_module(cls) -> ModuleType:
        return import_module_with_file_fallback(
            ModulePath.module_name_to_relative_file_path(cls.get_test_module_name())
        )

    @classmethod
    def get_test_module_content_with_skeletons(cls) -> str:
        test_module_content = get_module_content_as_str(cls.get_test_module())
        # if module content has no doctsring, add the default one
        if not starts_with_docstring(test_module_content):
            test_module_content = get_default_module_content() + test_module_content
        test_module_content = cls.get_test_module_content_with_func_skeletons(
            test_module_content
        )
        return cls.get_test_module_content_with_class_skeletons(test_module_content)

    @classmethod
    def get_test_module_content_with_func_skeletons(
        cls, test_module_content: str
    ) -> str:
        for test_func_name in cls.get_untested_func_names():
            test_module_content += cls.get_test_func_skeleton(test_func_name)
        return test_module_content

    @classmethod
    def get_untested_func_names(cls) -> list[str]:
        # get all functions from the source module
        funcs = get_all_functions_from_module(cls.get_src_module())
        # get all functions from the test module
        test_funcs = get_all_functions_from_module(cls.get_test_module())

        # get the theoretical test function names from the source functions
        supposed_test_func_names = [make_test_obj_name(f) for f in funcs]

        # get the actual test function names from the test module
        actual_test_func_names = [get_qualname_of_obj(f) for f in test_funcs]

        # get a list of all supposed test functions that are not in the test module
        untested_func_names = [
            f for f in supposed_test_func_names if f not in actual_test_func_names
        ]

        logger.debug(
            "Found %d untested functions: %s",
            len(untested_func_names),
            untested_func_names,
        )
        return untested_func_names

    @classmethod
    def get_test_func_skeleton(cls, test_func_name: str) -> str:
        return f'''

def {test_func_name}() -> None:
    """Test function."""
    raise {NotImplementedError.__name__}
'''

    @classmethod
    def get_test_module_content_with_class_skeletons(
        cls, test_module_content: str
    ) -> str:
        test_class_to_method_names = cls.get_untested_class_and_method_names()
        for (
            test_class_name,
            test_method_names,
        ) in test_class_to_method_names.items():
            test_cls_skeleton = cls.get_test_class_skeleton(test_class_name)
            test_cls_content = test_cls_skeleton
            for test_method_name in test_method_names:
                test_cls_content += cls.get_test_method_skeleton(test_method_name)

            # if the class already exists we need to insert the new methods
            # rather than overwrite the class
            module_content_parts = test_module_content.split(test_cls_skeleton)
            expected_parts = 2  # bc there should be only one or zero class definition
            num_parts = len(module_content_parts)
            if num_parts > expected_parts:
                msg = (
                    f"Found {num_parts} parts, expected {expected_parts}. "
                    f"This likely means the class {test_class_name} "
                    f"is defined multiple times in the test module."
                )
                raise ValueError(msg)
            # we simply insert the new class content into the parts
            module_content_parts.insert(1, test_cls_content)
            test_module_content = "".join(module_content_parts)

        return test_module_content

    @classmethod
    def get_untested_class_and_method_names(cls) -> defaultdict[str, list[str]]:
        # get all classes from the source module
        classes = get_all_cls_from_module(cls.get_src_module())
        # get all classes from the test module
        test_classes = get_all_cls_from_module(cls.get_test_module())

        # get all classes mapped to their methods from the source module
        class_to_methods = {
            c: get_all_methods_from_cls(c, exclude_parent_methods=True) for c in classes
        }
        # get all classes mapped to their methods from the test module
        test_class_to_test_methods = {
            tc: get_all_methods_from_cls(tc, exclude_parent_methods=True)
            for tc in test_classes
        }

        # get the theoretical test class names mapped to their test method names
        supposed_test_class_to_test_methods_names = {
            make_test_obj_name(c): [make_test_obj_name(m) for m in ms]
            for c, ms in class_to_methods.items()
        }
        # get the actual test class names mapped to their test method names
        actual_test_class_to_test_methods_names = {
            get_isolated_obj_name(tc): [get_isolated_obj_name(tm) for tm in tms]
            for tc, tms in test_class_to_test_methods.items()
        }

        # get a dict of all supposed test classes
        # mapped to their untested test method names
        untested_test_class_to_test_methods_names: defaultdict[str, list[str]] = (
            defaultdict(list)
        )
        for (
            supposed_test_class_name,
            supposed_test_methods_names,
        ) in supposed_test_class_to_test_methods_names.items():
            actual_test_methods_names = actual_test_class_to_test_methods_names.get(
                supposed_test_class_name, []
            )
            untested_test_methods_names = [
                tmn
                for tmn in supposed_test_methods_names
                if tmn not in actual_test_methods_names
            ]
            # add the test class name to the dict if there are untested methods
            # or if the test class is not in the test module at all
            if untested_test_methods_names or (
                supposed_test_class_name not in actual_test_class_to_test_methods_names
            ):
                untested_test_class_to_test_methods_names[supposed_test_class_name] = (
                    untested_test_methods_names
                )

        # will be an empty dict if all test classes and methods are implemented
        logger.debug(
            "Found %d untested classes: %s",
            len(untested_test_class_to_test_methods_names),
            untested_test_class_to_test_methods_names,
        )
        return untested_test_class_to_test_methods_names

    @classmethod
    def get_test_class_skeleton(cls, test_class_name: str) -> str:
        return f'''

class {test_class_name}:
    """Test class."""
'''

    @classmethod
    def get_test_method_skeleton(cls, test_method_name: str) -> str:
        return f'''
    def {test_method_name}(self) -> None:
        """Test method."""
        raise {NotImplementedError.__name__}
'''

    @classmethod
    def make_subclasses_for_modules(cls, modules: list[ModuleType]) -> list[type[Self]]:
        return cls.get_subclasses_ordered_by_priority(
            *[cls.make_subclass_for_module(module) for module in modules]
        )

    @classmethod
    def make_subclass_for_module(cls, module: ModuleType) -> type[Self]:
        test_module_name = cls.get_test_module_name_from_src_module(module).split(".")[
            -1
        ]

        test_cls_name = (
            make_name_from_obj(
                test_module_name, split_on="_", join_on="", capitalize=True
            )
            + cls.__name__
        )

        @classmethod
        def get_src_module(cls: type[Self]) -> ModuleType:  # noqa: ARG001
            return module

        subclass = type(
            test_cls_name,
            (cls,),
            {cls.get_src_module.__name__: get_src_module},
        )
        return cast("type[Self]", subclass)

    @classmethod
    def create_test_modules(cls, modules: list[ModuleType]) -> None:
        subclasses = cls.make_subclasses_for_modules(modules)
        cls.init_subclasses(*subclasses)
