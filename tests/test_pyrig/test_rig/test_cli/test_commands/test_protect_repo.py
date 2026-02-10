"""module."""

from pyrig.rig.cli.commands.protect_repo import (
    protect_repository,
)
from pyrig.rig.utils.testing import skip_if_no_internet


@skip_if_no_internet
def test_protect_repository() -> None:
    """Test func for protect_repository."""
    protect_repository()
