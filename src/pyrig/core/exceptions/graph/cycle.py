"""Exceptions related cycles in graphs."""

from pyrig.core.exceptions.base.graph import GraphError


class GraphCycleError(GraphError):
    """Raised when a cycle is detected in a graph."""

    def __init__(self) -> None:
        """Initialize the exception with a default message."""
        super().__init__("""A cycle was detected in the graph, which is not allowed.
This typically indicates a circular dependency.""")
