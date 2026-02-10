"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.dev.tools.version_controller import VersionController
from pyrig.dev.utils.version_control import (
    get_github_repo_token,
    path_is_in_ignore,
)


def test_get_github_repo_token() -> None:
    """Test func for get_github_token."""
    token = get_github_repo_token()
    assert isinstance(token, str), f"Expected token to be str, got {type(token)}"


def test_path_is_in_ignore(tmp_path: Path) -> None:
    """Test method."""
    with chdir(tmp_path):
        content = """# Comment line
*.pyc
__pycache__/
.venv/
# This is a comment
build/
dist/
*.egg-info/
.pytest_cache/
"""
        VersionController.L.get_ignore_path().write_text(content)
        assert path_is_in_ignore("folder/file.pyc")
        assert path_is_in_ignore("__pycache__/file.pdf")
        assert path_is_in_ignore(".venv/file.py")
        assert path_is_in_ignore("build/file.py")
        assert path_is_in_ignore("dist/file.py")
        assert path_is_in_ignore("folder/folder.egg-info/file.py")
