"""module."""

from pathlib import Path

from pyrig.rig.configs.issue_templates.feature_request import FeatureRequestConfigFile


class TestFeatureRequestConfigFile:
    """Test class."""

    def test_get_parent_path(self) -> None:
        """Test method."""
        result = FeatureRequestConfigFile.get_parent_path()
        assert result == Path(".github/ISSUE_TEMPLATE")

    def test__get_configs(self) -> None:
        """Test method."""
        result = FeatureRequestConfigFile._get_configs()  # noqa: SLF001
        assert isinstance(result, dict)

    def test_is_correct(self) -> None:
        """Test method."""
        assert FeatureRequestConfigFile().is_correct()
