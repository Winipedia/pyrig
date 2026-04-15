"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_class_
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from importlib import import_module
from typing import Any, ClassVar

from pyrig.core.introspection.classes import (
    all_cls_from_module,
    all_methods_from_cls,
    classproperty,
    discard_abstract_classes,
    discard_parent_classes,
    discard_parent_methods,
    discover_all_subclasses,
)
from pyrig.core.introspection.inspection import unwrapped_obj


def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorate a function for testing purposes."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Execute the wrapped function."""
        return func(*args, **kwargs)

    return wrapper


# Test classes for all_methods_from_cls
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


class TestClass(ParentClass):
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


def test_all_methods_from_cls() -> None:
    """Test function."""
    cls = TestClass
    methods = all_methods_from_cls(cls)
    method_names = [unwrapped_obj(m).__name__ for m in methods]
    expected_method_names = {
        ParentClass.parent_method.__name__,
        ParentClass.parent_static_method.__name__,
        ParentClass.parent_class_method.__name__,
        unwrapped_obj(ParentClass.parent_property).__name__,
        TestClass.instance_method.__name__,
        TestClass.static_method.__name__,
        TestClass.class_method.__name__,
        unwrapped_obj(TestClass.prop).__name__,
        TestClass._private_method.__name__,  # noqa: SLF001
        TestClass.decorated_method.__name__,
    }
    assert set(method_names) == expected_method_names


def test_all_cls_from_module() -> None:
    """Test function."""
    # use this file as the module
    module = import_module(test_all_cls_from_module.__module__)

    classes = all_cls_from_module(module)

    # expected classes in order of definition
    expected_classes: list[type] = [
        ParentClass,
        TestClass,
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
    subclasses = discover_all_subclasses(ParentClass)

    expected_subclasses: set[type] = {ParentClass, TestClass}

    for expected_subclass in expected_subclasses:
        assert expected_subclass in subclasses, (
            f"Expected {expected_subclass} in subclasses, got {subclasses}"
        )

    # Test with TestClass - should have no subclasses
    subclasses = discover_all_subclasses(TestClass)

    assert subclasses == {TestClass}, (
        f"Expected no subclasses for TestClass, got {subclasses}"
    )


def test_discard_parent_classes() -> None:
    """Test function."""
    classes = tuple(discard_parent_classes([ParentClass, TestClass]))
    assert ParentClass not in classes, f"Expected ParentClass not in {classes}"
    assert TestClass in classes, f"Expected TestClass in {classes}"


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
    cls = TestClass
    methods = list(all_methods_from_cls(cls))
    # check a parent method is in the list of methods before discarding
    assert ParentClass.parent_class_method.__name__ in [
        unwrapped_obj(m).__name__ for m in methods
    ]
    assert TestClass.class_method.__name__ in [
        unwrapped_obj(m).__name__ for m in methods
    ]
    # discard parent methods
    methods = list(discard_parent_methods(cls, methods))
    method_names = [unwrapped_obj(m).__name__ for m in methods]
    assert ParentClass.parent_class_method.__name__ not in method_names

    assert TestClass.class_method.__name__ in method_names
