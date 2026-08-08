"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_class_
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from importlib import import_module
from typing import ClassVar

from pyrig_runtime.core.introspection.inspection import obj_members

from pyrig.core.introspection.classes import (
    cls_methods,
    filter_direct_methods,
    filter_module_classes,
)
from pyrig.core.introspection.inspection import unwrap_obj


def decorator[R](func: Callable[..., R]) -> Callable[..., R]:
    """Decorate a function for testing purposes."""

    @wraps(func)
    def wrapper(*args: object, **kwargs: object) -> R:
        """Execute the wrapped function."""
        return func(*args, **kwargs)

    return wrapper


# Test classes for cls_methods
class ParentClass:
    """Parent class for testing inheritance."""

    class_var: ClassVar[str] = "parent_class_var"

    def parent_method(self) -> str:
        """Parent method."""
        return "parent_method"

    @staticmethod
    def parent_static_method() -> str:
        """Parent static method."""
        return "parent_static_method"

    @classmethod
    def parent_class_method(cls) -> str:
        """Parent class method."""
        return "parent_class_method"

    @property
    def parent_property(self) -> str:
        """Parent property."""
        return "parent_property"


class ChildTestClass(ParentClass):
    """Test class."""

    class_var: ClassVar[str] = "test_class_var"

    def instance_method(self) -> str:
        """Instance method."""
        return "instance_method"

    @staticmethod
    def static_method() -> str:
        """Return a static method value."""
        return "static_method"

    @classmethod
    def class_method(cls) -> str:
        """Class method."""
        return "class_method"

    @property
    def prop(self) -> str:
        """Property method."""
        return "property"

    def _private_method(self) -> str:
        """Private method."""
        return "private_method"

    @decorator
    def decorated_method(self) -> str:
        """Decorate with @decorator."""
        return "decorated_method"


class GrandchildTestClass(ChildTestClass):
    """Grandchild class for testing multiple levels of inheritance."""

    def grandchild_method(self) -> str:
        """Grandchild method."""
        return "grandchild_method"


class DecoratedClass:
    """Class with decorated methods for testing."""

    @decorator
    def decorated_method(self) -> str:
        """Return a decorated method value."""
        return "decorated_method"


class AbstractParent(ABC):
    """Abstract parent class for testing."""

    @abstractmethod
    def abstract_method(self) -> str:
        """Abstract method that must be implemented."""


class ConcreteChild(AbstractParent):
    """Concrete implementation of AbstractParent."""

    def __init__(self) -> None:
        """Initialize ConcreteChild."""
        super().__init__()

    def abstract_method(self) -> str:
        """Implement the abstract method."""
        return "concrete_implementation"


class AnotherAbstractChild(AbstractParent):
    """Another abstract child that doesn't implement the method."""

    @abstractmethod
    def another_abstract_method(self) -> str:
        """Another abstract method."""


def test_cls_methods() -> None:
    """Test function."""
    cls = ChildTestClass
    methods = cls_methods(cls)
    method_names = [unwrap_obj(m).__name__ for m in methods]
    expected_method_names = {
        ParentClass.parent_method.__name__,
        ParentClass.parent_static_method.__name__,
        ParentClass.parent_class_method.__name__,
        unwrap_obj(ParentClass.parent_property).__name__,
        ChildTestClass.instance_method.__name__,
        ChildTestClass.static_method.__name__,
        ChildTestClass.class_method.__name__,
        unwrap_obj(ChildTestClass.prop).__name__,
        ChildTestClass._private_method.__name__,  # noqa: SLF001
        ChildTestClass.decorated_method.__name__,
    }
    assert set(method_names) == expected_method_names


def test_filter_direct_methods() -> None:
    """Test function."""
    cls = ChildTestClass
    methods = list(cls_methods(cls))
    # check a parent method is in the list of methods before discarding
    assert ParentClass.parent_class_method.__name__ in [
        unwrap_obj(m).__name__ for m in methods
    ]
    assert ChildTestClass.class_method.__name__ in [
        unwrap_obj(m).__name__ for m in methods
    ]
    # discard parent methods
    methods = list(filter_direct_methods(cls, methods))
    method_names = [unwrap_obj(m).__name__ for m in methods]
    assert ParentClass.parent_class_method.__name__ not in method_names

    assert ChildTestClass.class_method.__name__ in method_names


def test_filter_module_classes() -> None:
    """Test function."""
    module = import_module(test_filter_module_classes.__module__)
    members = list(obj_members(module))
    classes = list(filter_module_classes(module, members))
    expected_classes: list[type] = [
        ParentClass,
        ChildTestClass,
        GrandchildTestClass,
        DecoratedClass,
        AbstractParent,
        ConcreteChild,
        AnotherAbstractChild,
    ]
    expected_classes_names: list[str] = [c.__name__ for c in expected_classes]
    classes_names = [c.__name__ for c in classes]
    assert set(classes_names) == set(expected_classes_names)
