"""module."""

from pathlib import Path

from pyrig.dev.configs.markdown.code_of_conduct import CodeOfConductConfigFile


class TestCodeOfConductConfigFile:
    """Test class."""

    def test_get_contributor_covenant_with_contact_method(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.get_contributor_covenant_with_contact_method()
        assert len(result) > 0

    def test_get_contact_method(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.get_contact_method()
        assert len(result) > 0

    def test_get_filename(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.get_filename()
        assert result == "CODE_OF_CONDUCT"

    def test_get_parent_path(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.get_parent_path()
        assert result == Path()

    def test_get_lines(self) -> None:
        """Test method."""
        lines = CodeOfConductConfigFile.get_lines()
        assert len(lines) > 0

    def test_is_correct(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.is_correct()
        assert result

    def test_get_contributor_covenant(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.get_contributor_covenant()
        assert len(result) > 0
