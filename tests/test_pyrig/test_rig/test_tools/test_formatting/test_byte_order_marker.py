"""Test module."""

from pyrig.rig.tools.formatting.byte_order_marker import ByteOrderMarkerFormatter
from pyrig.rig.tools.pyrigger import Pyrigger


class TestByteOrderMarkerFormatter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = ByteOrderMarkerFormatter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            ByteOrderMarkerFormatter.I.image_url()
            == "https://img.shields.io/badge/BOM-fix--byte--order--marker-orange"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            ByteOrderMarkerFormatter.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = ByteOrderMarkerFormatter.I.name()
        assert result == "fix-byte-order-marker"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = ByteOrderMarkerFormatter.I.dev_dependencies()
        assert result == ("pre-commit-hooks",)

    def test_format_args(self) -> None:
        """Test method."""
        result = ByteOrderMarkerFormatter.I.format_args()
        assert result == ("fix-byte-order-marker",)

    def test_format_hook(self) -> None:
        """Test method."""
        # runs first among the text-fixing hooks, right after sync
        hook = ByteOrderMarkerFormatter.I.format_hook()
        sync_hook = Pyrigger.I.synchronize_project_hook()
        assert hook["priority"] > sync_hook["priority"]
        assert hook["types"] == ["text"]

    def test_fix_byte_order_marker(self) -> None:
        """Test method."""
        assert (
            ByteOrderMarkerFormatter.I.fix_byte_order_marker()
            == ByteOrderMarkerFormatter.I.format_args()
        )
