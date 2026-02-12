"""module."""

from pyrig.rig.tools.package_index import PackageIndex


class TestPackageIndex:
    """Test class."""

    def test_get_name(self) -> None:
        """Test method."""
        result = PackageIndex.L.get_name()
        assert result == "pypi"

    def test_get_group(self) -> None:
        """Test method."""
        result = PackageIndex.L.get_group()
        assert isinstance(result, str)
        assert result == "project-info"

    def test_get_badge_urls(self) -> None:
        """Test method."""
        result = PackageIndex.L.get_badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_get_package_index_url(self) -> None:
        """Test method."""
        result = PackageIndex.L.get_package_index_url()
        assert isinstance(result, str)
        assert result.startswith("https://pypi.org/project/")

    def test_get_dev_dependencies(self) -> None:
        """Test method."""
        result = PackageIndex.L.get_dev_dependencies()
        assert result == []
