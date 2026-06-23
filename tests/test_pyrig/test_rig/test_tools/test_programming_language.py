"""module."""

from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.programming_language import ProgrammingLanguage


class TestProgrammingLanguage:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            ProgrammingLanguage().image_url()
            == "https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert ProgrammingLanguage.I.link_url() == "https://www.python.org"

    def test_version_control_ignore_paths(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().version_control_ignore_paths() == ("__pycache__/",)

    def test_standard_init_content(self) -> None:
        """Test method."""
        assert isinstance(ProgrammingLanguage().standard_init_content(), str)

    def test_no_bytecode_env_var(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().no_bytecode_env_var() == "PYTHONDONTWRITEBYTECODE"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().dev_dependencies() == ()

    def test_name(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().name() == "python"

    def test_group(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().group() == Group.PROJECT_INFO
