"""Test module."""

import pytest

from pyrig.core.exceptions.graph.cycle import GraphCycleError


class TestGraphCycleError:
    """Test class."""

    def test___init__(self) -> None:
        """Test method."""
        with pytest.raises(GraphCycleError) as exc_info:
            raise GraphCycleError
        assert (
            str(exc_info.value)
            == """A cycle was detected in the graph, which is not allowed.
This typically indicates a circular dependency."""
        )
