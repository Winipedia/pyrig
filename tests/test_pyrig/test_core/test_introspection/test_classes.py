"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_class_
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from importlib import import_module
from typing import Any, ClassVar

from pyrig.core.introspection.classes import (
    classproperty,
    cls_methods,
    discard_abstract_classes,
    discard_parent_classes,
    discard_parent_methods,
    module_classes,
)
from pyrig.core.introspection.inspection import unwrapped_obj
from pyrig.core.introspection.packages import discover_all_subclasses


def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorate a function for testing purposes."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
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
    method_names = [unwrapped_obj(m).__name__ for m in methods]
    expected_method_names = {
        ParentClass.parent_method.__name__,
        ParentClass.parent_static_method.__name__,
        ParentClass.parent_class_method.__name__,
        unwrapped_obj(ParentClass.parent_property).__name__,
        ChildTestClass.instance_method.__name__,
        ChildTestClass.static_method.__name__,
        ChildTestClass.class_method.__name__,
        unwrapped_obj(ChildTestClass.prop).__name__,
        ChildTestClass._private_method.__name__,  # noqa: SLF001
        ChildTestClass.decorated_method.__name__,
    }
    assert set(method_names) == expected_method_names


def test_module_classes() -> None:
    """Test function."""
    # use this file as the module
    module = import_module(test_module_classes.__module__)

    classes = module_classes(module)

    # expected classes in order of definition
    expected_classes: list[type] = [
        ParentClass,
        ChildTestClass,
        GrandchildTestClass,
        DecoratedClass,
        AbstractParent,
        ConcreteChild,
        AnotherAbstractChild,
        Testclassproperty,
    ]
    expected_classes_names: list[str] = [c.__name__ for c in expected_classes]
    classes_names = [c.__name__ for c in classes]
    assert set(classes_names) == set(expected_classes_names), (
        f"Expected classes {expected_classes_names}, got {classes_names}"
    )


def test_discover_all_subclasses() -> None:
    """Test func."""
    # Test with ParentClass - should find TestClass as subclass
    subclasses = set(discover_all_subclasses(ParentClass))

    expected_subclasses: set[type] = {ChildTestClass, GrandchildTestClass}

    assert subclasses == expected_subclasses

    # Test with TestClass - should have no subclasses
    subclasses = set(discover_all_subclasses(ChildTestClass))

    expected_subclasses: set[type] = {GrandchildTestClass}

    assert subclasses == expected_subclasses

    # Test with GrandchildTestClass - should have no subclasses
    subclasses = set(discover_all_subclasses(GrandchildTestClass))

    assert subclasses == set()


def test_discard_parent_classes() -> None:
    """Test function."""
    classes = tuple(discard_parent_classes([ParentClass, ChildTestClass]))
    assert ParentClass not in classes, f"Expected ParentClass not in {classes}"
    assert ChildTestClass in classes, f"Expected TestClass in {classes}"


class Testclassproperty:
    """Test class."""

    def test___init__(self) -> None:
        """Test that classproperty stores the function."""

        def func(cls: type) -> str:
            return cls.__name__

        prop = classproperty(func)
        assert prop.fget is func

    def test___get__(self) -> None:
        """Test that classproperty returns value from class."""

        class MyClass:
            @classproperty
            def name(cls: type) -> str:  # noqa: N805
                return cls.__name__.lower()

        # Access via class
        assert MyClass.name == "myclass"
        # Access via instance
        assert MyClass().name == "myclass"


def test_discard_abstract_classes() -> None:
    """Test function."""
    classes = tuple(
        discard_abstract_classes([AbstractParent, ConcreteChild, AnotherAbstractChild])
    )
    assert AbstractParent not in classes, f"Expected AbstractParent not in {classes}"
    assert AnotherAbstractChild not in classes, (
        f"Expected AnotherAbstractChild not in {classes}"
    )
    assert ConcreteChild in classes, f"Expected ConcreteChild in {classes}"


def test_discard_parent_methods() -> None:
    """Test function."""
    cls = ChildTestClass
    methods = list(cls_methods(cls))
    # check a parent method is in the list of methods before discarding
    assert ParentClass.parent_class_method.__name__ in [
        unwrapped_obj(m).__name__ for m in methods
    ]
    assert ChildTestClass.class_method.__name__ in [
        unwrapped_obj(m).__name__ for m in methods
    ]
    # discard parent methods
    methods = list(discard_parent_methods(cls, methods))
    method_names = [unwrapped_obj(m).__name__ for m in methods]
    assert ParentClass.parent_class_method.__name__ not in method_names

    assert ChildTestClass.class_method.__name__ in method_names
