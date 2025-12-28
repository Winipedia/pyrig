"""module."""

from contextlib import chdir
from pathlib import Path

from github.Repository import Repository

from pyrig.dev.cli.commands.protect_repo import get_default_ruleset_params
from pyrig.dev.utils.git import (
    DEFAULT_RULESET_NAME,
    GITIGNORE_PATH,
    create_or_update_ruleset,
    get_all_rulesets,
    get_github_repo_token,
    get_repo,
    get_rules_payload,
    github_api_request,
    load_gitignore,
    path_is_in_gitignore_lines,
    ruleset_exists,
)
from pyrig.src.git import (
    get_repo_owner_and_name_from_git,
)
from pyrig.src.testing.assertions import assert_with_msg


def test_get_rules_payload() -> None:
    """Test func for get_rules_payload."""
    # Test with no rules
    rules = get_rules_payload()
    assert_with_msg(
        rules == [],
        "Expected empty list when no rules provided",
    )

    # Test with single rule
    rules = get_rules_payload(deletion={})
    assert_with_msg(
        len(rules) == 1,
        "Expected one rule",
    )
    assert_with_msg(
        rules[0]["type"] == "deletion",
        f"Expected type 'deletion', got {rules[0]['type']}",
    )

    # Test with rule that has parameters
    rules = get_rules_payload(pull_request={"required_approving_review_count": 1})
    assert_with_msg(
        len(rules) == 1,
        "Expected one rule",
    )
    assert_with_msg(
        "parameters" in rules[0],
        "Expected 'parameters' key in rule",
    )
    assert_with_msg(
        rules[0]["parameters"]["required_approving_review_count"] == 1,
        "Expected parameter value to be 1",
    )

    # Test with multiple rules
    rules = get_rules_payload(
        deletion={},
        creation={},
        pull_request={"required_approving_review_count": 1},
    )
    expected_multiple_rules = 3
    assert_with_msg(
        len(rules) == expected_multiple_rules,
        f"Expected {expected_multiple_rules} rules, got {len(rules)}",
    )


def test_get_repo() -> None:
    """Test func for get_repo."""
    owner, repo_name = get_repo_owner_and_name_from_git()
    repo = get_repo(
        get_github_repo_token(),
        owner,
        repo_name,
    )
    assert_with_msg(
        isinstance(repo, Repository),
        "Expected Repository object",
    )
    assert_with_msg(
        repo.name == repo_name,
        f"Expected repo name {repo_name}, got {repo.name}",
    )


def test_get_all_rulesets() -> None:
    """Test func for get_all_rulesets."""
    rulesets = get_all_rulesets(
        get_github_repo_token(),
        *get_repo_owner_and_name_from_git(),
    )
    assert_with_msg(
        isinstance(rulesets, list),
        "Expected rulesets to be a list",
    )


def test_ruleset_exists() -> None:
    """Test func for ruleset_exists."""
    ruleset_id = ruleset_exists(
        get_github_repo_token(),
        *get_repo_owner_and_name_from_git(),
        DEFAULT_RULESET_NAME,
    )
    assert_with_msg(
        ruleset_id > 0,
        f"Expected ruleset id > 0, got {ruleset_id}",
    )


def test_create_or_update_ruleset() -> None:
    """Test func for create_or_update_ruleset."""
    token = get_github_repo_token()
    owner, repo_name = get_repo_owner_and_name_from_git()
    create_or_update_ruleset(
        token=token,
        owner=owner,
        repo_name=repo_name,
        **get_default_ruleset_params(),
    )


def test_get_github_repo_token() -> None:
    """Test func for get_github_token."""
    token = get_github_repo_token()
    assert_with_msg(
        isinstance(token, str), f"Expected token to be str, got {type(token)}"
    )


def test_github_api_request() -> None:
    """Test function."""
    github_api_request(
        get_github_repo_token(),
        *get_repo_owner_and_name_from_git(),
        "rulesets",
        method="GET",
    )


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
