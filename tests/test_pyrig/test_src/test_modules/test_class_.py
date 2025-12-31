"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_class_
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from typing import Any, ClassVar

from pyrig.src.modules.class_ import (
    discard_parent_classes,
    get_all_cls_from_module,
    get_all_methods_from_cls,
    get_all_subclasses,
    get_cached_instance,
)


def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorate a function for testing purposes."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Execute the wrapped function."""
        return func(*args, **kwargs)

    return wrapper


# Test classes for get_all_methods_from_cls
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


def test_get_all_methods_from_cls() -> None:
    """Test func for get_all_methods_from_cls."""
    # Test case 1: Get all methods excluding inherited methods
    methods = get_all_methods_from_cls(TestClass, exclude_parent_methods=True)

    # assert __annotate__ is not considered a method (3.14 introduces this injection)
    assert "__annotate__" not in [
        m.__name__ for m in methods if hasattr(m, "__name__")
    ], "Expected __annotate__ not to be considered a method"

    # expected methods in order of definition
    expected_methods = [
        TestClass.instance_method,
        TestClass.static_method,
        TestClass.class_method,
        TestClass.prop,
        TestClass._private_method,  # noqa: SLF001
        TestClass.decorated_method,
    ]
    assert methods == expected_methods, (
        f"Expected methods {expected_methods}, got {methods}"
    )

    # Test case 2: Get all methods including inherited methods
    methods = get_all_methods_from_cls(TestClass, exclude_parent_methods=False)

    # expected methods in order of definition
    expected_methods = [
        ParentClass.parent_method,
        ParentClass.parent_static_method,
        TestClass.parent_class_method,  # bound by accessed class
        ParentClass.parent_property,
        TestClass.instance_method,
        TestClass.static_method,
        TestClass.class_method,
        TestClass.prop,
        TestClass._private_method,  # noqa: SLF001
        TestClass.decorated_method,
    ]
    assert methods == expected_methods, (
        f"Expected methods {expected_methods}, got {methods}"
    )


def test_get_all_cls_from_module() -> None:
    """Test func for get_all_cls_from_module."""
    # use this file as the module
    module = test_get_all_cls_from_module.__module__

    classes = get_all_cls_from_module(module)

    # expected classes in order of definition
    expected_classes: list[type] = [
        ParentClass,
        TestClass,
        DecoratedClass,
        AbstractParent,
        ConcreteChild,
        AnotherAbstractChild,
    ]
    expected_classes_names: list[str] = [c.__name__ for c in expected_classes]
    classes_names = [c.__name__ for c in classes]
    assert classes_names == expected_classes_names, (
        f"Expected classes {expected_classes_names}, got {classes_names}"
    )


def test_get_all_subclasses() -> None:
    """Test func for get_all_subclasses."""
    # Test with ParentClass - should find TestClass as subclass
    subclasses = get_all_subclasses(ParentClass)

    expected_subclasses: set[type] = {ParentClass, TestClass}

    for expected_subclass in expected_subclasses:
        assert expected_subclass in subclasses, (
            f"Expected {expected_subclass} in subclasses, got {subclasses}"
        )

    # Test with TestClass - should have no subclasses
    subclasses = get_all_subclasses(TestClass)

    assert subclasses == {TestClass}, (
        f"Expected no subclasses for TestClass, got {subclasses}"
    )

    # test with discard_parents
    subclasses = get_all_subclasses(ParentClass, discard_parents=True)
    assert ParentClass not in subclasses, f"Expected ParentClass not in {subclasses}"
    assert TestClass in subclasses, f"Expected TestClass in {subclasses}"


def test_discard_parent_classes() -> None:
    """Test func for discard_parent_classes."""
    classes = discard_parent_classes([ParentClass, TestClass])
    assert ParentClass not in classes, f"Expected ParentClass not in {classes}"
    assert TestClass in classes, f"Expected TestClass in {classes}"


def test_get_cached_instance() -> None:
    """Test function."""

    class TestClass:
        """Test class."""

    instance1 = get_cached_instance(TestClass)
    instance2 = get_cached_instance(TestClass)
    assert instance1 is instance2
