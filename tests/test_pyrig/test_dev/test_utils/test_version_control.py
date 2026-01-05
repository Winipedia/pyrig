"""module."""

from contextlib import chdir
from pathlib import Path

import pyrig
from pyrig.dev.utils.version_control import (
    GITIGNORE_PATH,
    get_diff_from_version_control,
    get_github_repo_token,
    get_repo_owner_and_name_from_version_control,
    get_repo_remote_from_version_control,
    get_username_from_version_control,
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


def test_get_repo_remote_from_version_control() -> None:
    """Test func."""
    url = get_repo_remote_from_version_control()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"

    assert "github.com" in url, f"Expected 'github.com' in url, got {url}"


def test_get_repo_owner_and_name_from_version_control() -> None:
    """Test func for get_repo_owner_and_name_from_git."""
    owner, repo = get_repo_owner_and_name_from_version_control()
    assert isinstance(owner, str), f"Expected owner to be str, got {type(owner)}"

    assert owner == "Winipedia", f"Expected owner to be 'Winipedia', got {owner}"
    assert repo == pyrig.__name__, f"Expected repo to be 'pyrig', got {repo}"


def test_get_username_from_version_control() -> None:
    """Test function."""
    username = get_username_from_version_control()
    assert isinstance(username, str), (
        f"Expected username to be str, got {type(username)}"
    )
    assert len(username) > 0, "Expected username to be non-empty"


def test_get_diff_from_version_control() -> None:
    """Test function."""
    assert isinstance(get_diff_from_version_control(), str), (
        "Expected get_git_unstaged_changes to return str"
    )
