"""module."""

from pyrig.rig.tools.linting.python import PythonLinter


class TestPythonLinter:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            PythonLinter.I.image_url()
            == "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert PythonLinter.I.link_url() == "https://github.com/astral-sh/ruff"

    def test_version_control_ignore_paths(self) -> None:
        """Test method."""
        assert PythonLinter.I.version_control_ignore_paths() == (".ruff_cache/",)

    def test_extension(self) -> None:
        """Test method."""
        assert PythonLinter.I.extension() == "py"

    def test_regex(self) -> None:
        """Test method."""
        assert PythonLinter.I.regex() == r"\.pyi?$"

    def test_pydocstyle(self) -> None:
        """Test method."""
        assert PythonLinter.I.pydocstyle() == "google"

    def test_group(self) -> None:
        """Test method."""
        result = PythonLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_name(self) -> None:
        """Test method."""
        result = PythonLinter.I.name()
        assert result == "ruff"

    def test_check_args(self) -> None:
        """Test method."""
        result = PythonLinter.I.check_args()
        assert result == ("ruff", "check")

    def test_check_fix_args(self) -> None:
        """Test method."""
        result = PythonLinter.I.check_fix_args()
        assert result == ("ruff", "check", "--fix")

    def test_format_args(self) -> None:
        """Test method."""
        result = PythonLinter.I.format_args()
        assert result == ("ruff", "format")
