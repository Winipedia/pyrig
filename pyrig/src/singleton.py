"""Singleton pattern implementation using metaclasses.

This module provides a metaclass-based approach to implementing the Singleton
pattern in Python, ensuring that only one instance of a class exists throughout
the application lifecycle.
"""

from abc import ABCMeta
from typing import Any, ClassVar


class SingletonMeta(ABCMeta):
    """Metaclass that enforces the Singleton pattern.

    This metaclass ensures that only one instance of a class using this metaclass
    is created. Subsequent instantiation attempts return the same instance. It also
    provides a mechanism to clear cached instances when needed.

    Attributes:
        _instances: A dictionary mapping singleton classes to their sole instances.
    """

    _instances: ClassVar[dict["SingletonMeta", "Singleton"]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> "Singleton":
        """Create or retrieve the singleton instance.

        If this is the first call for the given class, a new instance is created
        and stored. Subsequent calls return the cached instance, regardless of the
        arguments provided.

        Args:
            *args: Positional arguments to pass to the class constructor (used only
                on first instantiation).
            **kwargs: Keyword arguments to pass to the class constructor (used only
                on first instantiation).

        Returns:
            The singleton instance of the class.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def clear(cls) -> None:
        """Remove the singleton instance for the given class.

        This method clears the cached instance, allowing a new instance to be
        created on the next instantiation. Useful for testing or when resetting
        the application state.
        """
        cls._instances.pop(cls, None)


class Singleton(metaclass=SingletonMeta):
    """Base class for creating singleton classes.

    Classes that inherit from Singleton will automatically have the Singleton
    pattern applied via the SingletonMeta metaclass. Subclasses will only have
    one instance throughout the application lifecycle.

    Example:
        >>> class MyService(Singleton):
        ...     pass
        >>> service1 = MyService()
        >>> service2 = MyService()
        >>> service1 is service2
        True
    """
