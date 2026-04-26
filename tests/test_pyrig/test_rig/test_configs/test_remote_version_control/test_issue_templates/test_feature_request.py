"""module."""

from pathlib import Path

from pyrig.rig.configs.remote_version_control.issue_templates.feature_request import (
    FeatureRequestConfigFile,
)


class TestFeatureRequestConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        assert FeatureRequestConfigFile.I.stem() == "feature_request"

    def test_parent_path(self) -> None:
        """Test method."""
        result = FeatureRequestConfigFile.I.parent_path()
        assert result == Path(".github/ISSUE_TEMPLATE")

    def test__configs(self) -> None:
        """Test method."""
        result = FeatureRequestConfigFile.I._configs()  # noqa: SLF001
        assert isinstance(result, dict)
