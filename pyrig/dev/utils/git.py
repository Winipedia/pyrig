"""GitHub repository API utilities and ruleset management.

This module provides low-level utilities for interacting with the GitHub API,
specifically for repository rulesets. It uses the PyGithub library for
authentication and API calls.

Rulesets are GitHub's newer mechanism for branch protection, offering more
flexibility than the older branch protection rules. This module provides
functions to create, update, and query rulesets.

Attributes:
    DEFAULT_BRANCH: The default branch name used by pyrig ("main").
    DEFAULT_RULESET_NAME: The name of the default protection ruleset.

Example:
    >>> from pyrig.src.git.github.repo.repo import get_repo, create_or_update_ruleset
    >>> repo = get_repo(token, "owner", "repo_name")
    >>> rules = get_rules_payload(pull_request={"required_approving_review_count": 1})
"""

import logging
import os
from pathlib import Path
from typing import Any, Literal

from dotenv import dotenv_values
from github import Github
from github.Auth import Token
from github.Repository import Repository

logger = logging.getLogger(__name__)

DEFAULT_BRANCH = "main"

DEFAULT_RULESET_NAME = f"{DEFAULT_BRANCH} protection"


def get_rules_payload(  # noqa: PLR0913
    *,
    creation: dict[str, Any] | None = None,
    update: dict[str, Any] | None = None,
    deletion: dict[str, Any] | None = None,
    required_linear_history: dict[str, Any] | None = None,
    merge_queue: dict[str, Any] | None = None,
    required_deployments: dict[str, Any] | None = None,
    required_signatures: dict[str, Any] | None = None,
    pull_request: dict[str, Any] | None = None,
    required_status_checks: dict[str, Any] | None = None,
    non_fast_forward: dict[str, Any] | None = None,
    commit_message_pattern: dict[str, Any] | None = None,
    commit_author_email_pattern: dict[str, Any] | None = None,
    committer_email_pattern: dict[str, Any] | None = None,
    branch_name_pattern: dict[str, Any] | None = None,
    tag_name_pattern: dict[str, Any] | None = None,
    file_path_restriction: dict[str, Any] | None = None,
    max_file_path_length: dict[str, Any] | None = None,
    file_extension_restriction: dict[str, Any] | None = None,
    max_file_size: dict[str, Any] | None = None,
    workflows: dict[str, Any] | None = None,
    code_scanning: dict[str, Any] | None = None,
    copilot_code_review: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build a rules array for a GitHub ruleset.

    Args:
        creation: Only allow users with bypass permission to create matching
            refs.
        update: Only allow users with bypass permission to update matching
            refs.
        deletion: Only allow users with bypass permissions to delete matching
            refs.
        required_linear_history: Prevent merge commits from being pushed to
            matching refs.
        merge_queue: Merges must be performed via a merge queue.
        required_deployments: Choose which environments must be successfully
            deployed to before refs can be pushed.
        required_signatures: Commits pushed to matching refs must have verified
            signatures.
        pull_request: Require all commits be made to a non-target branch and
            submitted via a pull request.
        required_status_checks: Choose which status checks must pass before the
            ref is updated.
        non_fast_forward: Prevent users with push access from force pushing to
            refs.
        commit_message_pattern: Parameters to be used for the
            commit_message_pattern rule.
        commit_author_email_pattern: Parameters to be used for the
            commit_author_email_pattern rule.
        committer_email_pattern: Parameters to be used for the
            committer_email_pattern rule.
        branch_name_pattern: Parameters to be used for the branch_name_pattern
            rule.
        tag_name_pattern: Parameters to be used for the tag_name_pattern rule.
        file_path_restriction: Prevent commits that include changes in
            specified file and folder paths.
        max_file_path_length: Prevent commits that include file paths that
            exceed the specified character limit.
        file_extension_restriction: Prevent commits that include files with
            specified file extensions.
        max_file_size: Prevent commits with individual files that exceed the
            specified limit.
        workflows: Require all changes made to a targeted branch to pass the
            specified workflows.
        code_scanning: Choose which tools must provide code scanning results
            before the reference is updated.
        copilot_code_review: Request Copilot code review for new pull requests
            automatically.

    Returns:
        A list of rule objects to be used in a GitHub ruleset.
    """
    rules: list[dict[str, Any]] = []

    rule_map = {
        "creation": creation,
        "update": update,
        "deletion": deletion,
        "required_linear_history": required_linear_history,
        "merge_queue": merge_queue,
        "required_deployments": required_deployments,
        "required_signatures": required_signatures,
        "pull_request": pull_request,
        "required_status_checks": required_status_checks,
        "non_fast_forward": non_fast_forward,
        "commit_message_pattern": commit_message_pattern,
        "commit_author_email_pattern": commit_author_email_pattern,
        "committer_email_pattern": committer_email_pattern,
        "branch_name_pattern": branch_name_pattern,
        "tag_name_pattern": tag_name_pattern,
        "file_path_restriction": file_path_restriction,
        "max_file_path_length": max_file_path_length,
        "file_extension_restriction": file_extension_restriction,
        "max_file_size": max_file_size,
        "workflows": workflows,
        "code_scanning": code_scanning,
        "copilot_code_review": copilot_code_review,
    }

    for rule_type, rule_config in rule_map.items():
        if rule_config is not None:
            rule_obj: dict[str, Any] = {"type": rule_type}
            if rule_config:  # If there are parameters
                rule_obj["parameters"] = rule_config
            rules.append(rule_obj)

    return rules


def create_or_update_ruleset(  # noqa: PLR0913
    token: str,
    owner: str,
    repo_name: str,
    *,
    ruleset_name: str,
    enforcement: Literal["active", "disabled", "evaluate"] = "active",
    target: Literal["branch", "tag", "push"] = "branch",
    bypass_actors: list[dict[str, Any]] | None = None,
    conditions: dict[
        Literal["ref_name"], dict[Literal["include", "exclude"], list[str]]
    ]
    | None = None,
    rules: list[dict[str, Any]] | None = None,
) -> Any:
    """Create or update a repository ruleset.

    If a ruleset with the given name exists, it is updated. Otherwise,
    a new ruleset is created.

    Args:
        token: GitHub API token with repo permissions.
        owner: Repository owner (user or organization).
        repo_name: Repository name.
        ruleset_name: Name for the ruleset.
        enforcement: Enforcement level ("active", "disabled", or "evaluate").
        target: What the ruleset applies to ("branch", "tag", or "push").
        bypass_actors: List of actors who can bypass the ruleset.
        conditions: Branch/tag name patterns to include or exclude.
        rules: List of rule objects from `get_rules_payload()`.

    Returns:
        The API response containing the created/updated ruleset.
    """
    repo = get_repo(token, owner, repo_name)
    ruleset_id = ruleset_exists(
        token=token, owner=owner, repo_name=repo_name, ruleset_name=ruleset_name
    )
    method = "PUT" if ruleset_id else "POST"
    url = f"{repo.url}/rulesets"

    if ruleset_id:
        url += f"/{ruleset_id}"

    payload: dict[str, Any] = {
        "name": ruleset_name,
        "enforcement": enforcement,
        "target": target,
        "conditions": conditions,
        "rules": rules,
    }
    if bypass_actors:
        payload["bypass_actors"] = bypass_actors

    _headers, res = repo._requester.requestJsonAndCheck(  # noqa: SLF001
        method,
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        input=payload,
    )

    return res


def get_all_rulesets(token: str, owner: str, repo_name: str) -> Any:
    """Retrieve all rulesets defined for a repository.

    Args:
        token: GitHub API token.
        owner: Repository owner.
        repo_name: Repository name.

    Returns:
        A list of ruleset objects from the GitHub API.
    """
    repo = get_repo(token, owner, repo_name)
    url = f"{repo.url}/rulesets"
    method = "GET"
    _headers, res = repo._requester.requestJsonAndCheck(  # noqa: SLF001
        method,
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    return res


def get_repo(token: str, owner: str, repo_name: str) -> Repository:
    """Get a PyGithub Repository object for API operations.

    Args:
        token: GitHub API token.
        owner: Repository owner (user or organization).
        repo_name: Repository name.

    Returns:
        A PyGithub Repository object.
    """
    auth = Token(token)
    github = Github(auth=auth)
    return github.get_repo(f"{owner}/{repo_name}")


def ruleset_exists(token: str, owner: str, repo_name: str, ruleset_name: str) -> int:
    """Check if a ruleset with the given name exists.

    Args:
        token: GitHub API token.
        owner: Repository owner.
        repo_name: Repository name.
        ruleset_name: Name of the ruleset to check for.

    Returns:
        The ruleset ID if it exists, 0 otherwise.
    """
    rulesets = get_all_rulesets(token, owner, repo_name)
    main_ruleset = next((rs for rs in rulesets if rs["name"] == ruleset_name), None)
    return main_ruleset["id"] if main_ruleset else 0


def get_github_repo_token() -> str:
    """Retrieve the GitHub repository token for API authentication.

    Attempts to find a GitHub token in the following order:
    1. The `REPO_TOKEN` environment variable
    2. The `REPO_TOKEN` key in the project's `.env` file

    This priority order ensures CI/CD environments (which typically set
    environment variables) work seamlessly while allowing local development
    to use .env files.

    Returns:
        The GitHub token string.

    Raises:
        ValueError: If no token is found in either location, or if the
            .env file doesn't exist when falling back to it.

    Note:
        The token should have appropriate permissions for the intended
        operations (e.g., repo scope for branch protection rules).
    """
    # try os env first
    token = os.getenv("REPO_TOKEN")
    if token:
        return token

    # try .env next
    dotenv_path = Path(".env")
    if not dotenv_path.exists():
        msg = f"Expected {dotenv_path} to exist"
        raise ValueError(msg)
    dotenv = dotenv_values(dotenv_path)
    token = dotenv.get("REPO_TOKEN")
    if token:
        return token

    msg = f"Expected REPO_TOKEN in {dotenv_path}"
    raise ValueError(msg)
