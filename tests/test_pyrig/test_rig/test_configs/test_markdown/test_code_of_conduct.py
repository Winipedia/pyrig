"""module."""

from pathlib import Path

from pyrig.rig.configs.markdown.code_of_conduct import CodeOfConductConfigFile


class TestCodeOfConductConfigFile:
    """Test class."""

    def test_contributor_covenant_with_contact_method(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.I.contributor_covenant_with_contact_method()
        assert len(result) > 0

    def test_contact_method(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.I.contact_method()
        assert len(result) > 0

    def test_filename(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.I.filename()
        assert result == "CODE_OF_CONDUCT"

    def test_parent_path(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.I.parent_path()
        assert result == Path()

    def test_lines(self) -> None:
        """Test method."""
        lines = CodeOfConductConfigFile.I.lines()
        assert len(lines) > 0

    def test_is_correct(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.I.is_correct()
        assert result

    def test_contributor_covenant(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.I.contributor_covenant()
        assert len(result) > 0
