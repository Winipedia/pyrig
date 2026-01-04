"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.dev.utils.git import (
    GITIGNORE_PATH,
    get_github_repo_token,
    load_gitignore,
    path_is_in_gitignore_lines,
)


def test_get_github_repo_token() -> None:
    """Test func for get_github_token."""
    token = get_github_repo_token()
    assert isinstance(token, str), f"Expected token to be str, got {type(token)}"


def test_path_is_in_gitignore_lines(tmp_path: Path) -> None:
    """Test func for path_is_in_gitignore."""
    with chdir(tmp_path):
        content = """
# Comment line
*.pyc
__pycache__/
.venv/
# This is a comment
build/
dist/
*.egg-info/
.pytest_cache/
"""
        GITIGNORE_PATH.write_text(content)
        gitignore_lines = load_gitignore()
        assert path_is_in_gitignore_lines(gitignore_lines, "folder/file.pyc")

        assert path_is_in_gitignore_lines(gitignore_lines, "__pycache__/file.pdf")
        assert path_is_in_gitignore_lines(gitignore_lines, ".venv/file.py")
        assert path_is_in_gitignore_lines(gitignore_lines, "build/file.py")
        assert path_is_in_gitignore_lines(gitignore_lines, "dist/file.py")
        assert path_is_in_gitignore_lines(
            gitignore_lines, "folder/folder.egg-info/file.py"
        )


def test_load_gitignore(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        content = """
# Comment line
*.pyc
__pycache__/
.venv/
# This is a comment
build/
dist/
*.egg-info/
.pytest_cache/
"""
        GITIGNORE_PATH.write_text(content)
        assert load_gitignore() == content.splitlines()
