"""module."""

from pyrig.rig.tools.package_index import PackageIndex


class TestPackageIndex:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = PackageIndex.L.name()
        assert result == "pypi"

    def test_group(self) -> None:
        """Test method."""
        result = PackageIndex.L.group()
        assert isinstance(result, str)
        assert result == "project-info"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = PackageIndex.L.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_get_package_index_url(self) -> None:
        """Test method."""
        result = PackageIndex.L.get_package_index_url()
        assert isinstance(result, str)
        assert result.startswith("https://pypi.org/project/")

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = PackageIndex.L.dev_dependencies()
        assert result == []
