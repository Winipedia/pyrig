"""GitHub API utilities and repository ruleset management.

Utilities for interacting with the GitHub API, specifically for repository rulesets.
Uses PyGithub for authentication and API calls.

Functions:
    create_or_update_ruleset: Create or update a GitHub repository ruleset
    get_all_rulesets: Retrieve all rulesets defined for a repository
    get_repo: Get a PyGithub Repository object for API operations
    ruleset_exists: Check if a ruleset with the given name exists
    github_api_request: Make a generic GitHub API request for a repository

See Also:
    pyrig.dev.cli.commands.protect_repo: CLI command using these utilities
    pyrig.dev.utils.version_control: GitHub token retrieval and related constants
"""

import logging
from typing import Any, Literal

from github import Github
from github.Auth import Token
from github.Repository import Repository

logger = logging.getLogger(__name__)


def create_or_update_ruleset(
    token: str, owner: str, repo_name: str, **ruleset_params: Any
) -> Any:
    """Create or update a GitHub repository ruleset.

    Checks if a ruleset with the specified name exists. If yes, updates it;
    otherwise, creates a new one. Handles idempotent creation/update pattern.

    Args:
        token: GitHub API token with repo administration permissions (repo scope).
        owner: Repository owner username or organization name.
        repo_name: Repository name (without owner prefix).
        **ruleset_params: Ruleset configuration for GitHub API. Must include "name".
            Common parameters: name (str), target (str), enforcement (str),
            rules (list), conditions (dict), bypass_actors (list).

    Returns:
        API response dictionary with ruleset data (ID, name, rules, etc.).

    Raises:
        KeyError: If "name" not in ruleset_params.
        github.GithubException: If API request fails.

    Examples:
        Create a new ruleset::

            >>> create_or_update_ruleset(
            ...     token="ghp_...", owner="myorg", repo_name="myrepo",
            ...     name="main-protection", target="branch",
            ...     enforcement="active", rules=[{"type": "deletion"}]
            ... )
    """
    logger.info("Creating or updating ruleset: %s", ruleset_params["name"])
    ruleset_name: str = ruleset_params["name"]
    logger.debug(
        "Checking if ruleset '%s' exists for %s/%s", ruleset_name, owner, repo_name
    )
    ruleset_id = ruleset_exists(
        token=token, owner=owner, repo_name=repo_name, ruleset_name=ruleset_name
    )

    endpoint = "rulesets"
    if ruleset_id:
        logger.debug("Updating existing ruleset: %s (ID: %s)", ruleset_name, ruleset_id)
        endpoint += f"/{ruleset_id}"
    else:
        logger.debug("Creating new ruleset: %s", ruleset_name)

    result = github_api_request(
        token,
        owner,
        repo_name,
        endpoint=endpoint,
        method="PUT" if ruleset_id else "POST",
        payload=ruleset_params,
    )
    logger.info(
        "Ruleset '%s' %s successfully",
        ruleset_name,
        "updated" if ruleset_id else "created",
    )
    return result


def get_all_rulesets(token: str, owner: str, repo_name: str) -> Any:
    """Retrieve all rulesets defined for a repository.

    Fetches all repository rulesets regardless of target or enforcement level.

    Args:
        token: GitHub API token with repository read permissions.
        owner: Repository owner username or organization name.
        repo_name: Repository name (without owner prefix).

    Returns:
        List of ruleset dictionaries with metadata (id, name, target, enforcement,
        rules, etc.). Empty list if no rulesets defined.

    Raises:
        github.GithubException: If API request fails.

    Examples:
        Get all rulesets::

            >>> rulesets = get_all_rulesets(
            ...     token="ghp_...", owner="myorg", repo_name="myrepo"
            ... )
            >>> for rs in rulesets:
            ...     print(f"{rs['name']}: {rs['enforcement']}")
    """
    return github_api_request(
        token, owner, repo_name, endpoint="rulesets", method="GET"
    )


def get_repo(token: str, owner: str, repo_name: str) -> Repository:
    """Get a PyGithub Repository object for API operations.

    Creates an authenticated PyGithub client and retrieves a Repository object.

    Args:
        token: GitHub API token for authentication.
        owner: Repository owner username or organization name.
        repo_name: Repository name (without owner prefix).

    Returns:
        github.Repository.Repository object for API operations.

    Raises:
        github.UnknownObjectException: If repository doesn't exist or no access.
        github.BadCredentialsException: If token is invalid or expired.

    Examples:
        Get a repository object::

            >>> repo = get_repo(token="ghp_...", owner="myorg", repo_name="myrepo")
            >>> print(repo.full_name)
            'myorg/myrepo'
    """
    auth = Token(token)
    github = Github(auth=auth)
    return github.get_repo(f"{owner}/{repo_name}")


def ruleset_exists(token: str, owner: str, repo_name: str, ruleset_name: str) -> int:
    """Check if a ruleset with the given name exists in a repository.

    Searches all rulesets to find one matching the specified name.

    Args:
        token: GitHub API token with repository read permissions.
        owner: Repository owner username or organization name.
        repo_name: Repository name (without owner prefix).
        ruleset_name: Name of the ruleset (case-sensitive exact match).

    Returns:
        Ruleset ID (positive integer) if found, or 0 if not found.

    Raises:
        github.GithubException: If API request fails.

    Examples:
        Check if a ruleset exists::

            >>> ruleset_id = ruleset_exists(
            ...     token="ghp_...", owner="myorg", repo_name="myrepo",
            ...     ruleset_name="main-protection"
            ... )
            >>> if ruleset_id:
            ...     print(f"Ruleset exists with ID: {ruleset_id}")

    Note:
        Returns 0 (falsy) when not found, convenient for boolean checks.
    """
    rulesets = get_all_rulesets(token, owner, repo_name)
    main_ruleset = next((rs for rs in rulesets if rs["name"] == ruleset_name), None)
    return main_ruleset["id"] if main_ruleset else 0


def github_api_request(  # noqa: PLR0913
    token: str,
    owner: str,
    repo_name: str,
    endpoint: str,
    *,
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "GET",
    payload: dict[str, Any] | None = None,
) -> Any:
    """Make a generic GitHub API request for a repository.

    Performs an authenticated HTTP request using PyGithub's internal requester.
    Provides low-level interface for endpoints not fully supported by PyGithub.

    Args:
        token: GitHub API token for authentication.
        owner: Repository owner username or organization name.
        repo_name: Repository name (without owner prefix).
        endpoint: API endpoint path relative to repository URL (e.g., "rulesets",
            "pages"). Do not include leading slash.
        method: HTTP method. Defaults to "GET".
        payload: Optional dict to send as JSON. Used for POST, PUT, PATCH.

    Returns:
        Parsed JSON response as dict or list.

    Raises:
        github.GithubException: If API request fails.

    Examples:
        Get all rulesets::

            >>> rulesets = github_api_request(
            ...     token="ghp_...", owner="myorg", repo_name="myrepo",
            ...     endpoint="rulesets", method="GET"
            ... )

    Note:
        Uses PyGithub's internal `_requester` with automatic API version header.
    """
    logger.debug("GitHub API request: %s %s/%s/%s", method, owner, repo_name, endpoint)
    repo = get_repo(token, owner, repo_name)
    url = f"{repo.url}/{endpoint}"

    _headers, res = repo._requester.requestJsonAndCheck(  # noqa: SLF001
        method,
        url,
        input=payload,
    )
    logger.debug("GitHub API request successful: %s %s", method, endpoint)
    return res
