"""GitHub API utilities for repository management.

Provides authenticated access to the GitHub API using PyGithub, supporting
repository ruleset operations and arbitrary REST endpoint requests.
"""

import logging
from typing import TYPE_CHECKING, Any, Literal

from github import Github
from github.Auth import Token

if TYPE_CHECKING:
    from github.Repository import Repository

logger = logging.getLogger(__name__)


def create_or_update_ruleset(
    token: str, owner: str, repo_name: str, **ruleset_params: Any
) -> Any:
    """Create or update a GitHub repository ruleset.

    Checks whether a ruleset with the given name already exists on the repository.
    If it does, the existing ruleset is updated in place; otherwise a new one is
    created. The ``name`` key is required in ``ruleset_params`` to identify the
    target ruleset.

    Args:
        token: GitHub personal access token with repository administration
            permissions (``repo`` scope or ``administration:write``).
        owner: Repository owner — a GitHub username or organization name.
        repo_name: Repository name without the owner prefix.
        **ruleset_params: Ruleset configuration forwarded to the GitHub API.
            Must include ``name`` (str). Other common keys:
            ``target`` (str), ``enforcement`` (str), ``rules`` (list),
            ``conditions`` (dict), ``bypass_actors`` (list).

    Returns:
        Parsed JSON response from the GitHub API containing the created or
        updated ruleset data, including its ``id``, ``name``, and ``rules``.

    Raises:
        KeyError: If ``name`` is not provided in ``ruleset_params``.
        github.GithubException: If the API request fails.

    Examples:
        >>> create_or_update_ruleset(
        ...     token="ghp_...", owner="myorg", repo_name="myrepo",
        ...     name="main-protection", target="branch",
        ...     enforcement="active", rules=[{"type": "deletion"}],
        ... )
    """
    logger.debug("Creating or updating ruleset: %s", ruleset_params["name"])
    ruleset_name: str = ruleset_params["name"]
    logger.debug(
        "Checking if ruleset '%s' exists for %s/%s", ruleset_name, owner, repo_name
    )
    ruleset_id = ruleset_exists(
        token=token, owner=owner, repo_name=repo_name, ruleset_name=ruleset_name
    )

    endpoint = "rulesets"
    if ruleset_id:
        endpoint += f"/{ruleset_id}"

    action = "Updating" if ruleset_id else "Creating"
    logger.debug("%s ruleset: %s", action, ruleset_name)

    result = github_api_request(
        token,
        owner,
        repo_name,
        endpoint=endpoint,
        method="PUT" if ruleset_id else "POST",
        payload=ruleset_params,
    )
    logger.debug(
        "Ruleset '%s' %s successfully",
        ruleset_name,
        "updated" if ruleset_id else "created",
    )
    return result


def ruleset_exists(token: str, owner: str, repo_name: str, ruleset_name: str) -> int:
    """Check if a ruleset with the given name exists in a repository.

    Fetches all rulesets for the repository and searches for an exact name match.

    Args:
        token: GitHub API token with repository read permissions.
        owner: Repository owner — a GitHub username or organization name.
        repo_name: Repository name without the owner prefix.
        ruleset_name: Name of the ruleset to look for (case-sensitive).

    Returns:
        The ruleset ID (a positive integer) if found, or ``0`` if not found.
        Because ``0`` is falsy, the return value can be used directly in an
        ``if`` statement to check existence.

    Raises:
        github.GithubException: If the API request fails.

    Examples:
        >>> ruleset_id = ruleset_exists(
        ...     token="ghp_...", owner="myorg", repo_name="myrepo",
        ...     ruleset_name="main-protection",
        ... )
        >>> if ruleset_id:
        ...     print(f"Ruleset exists with ID: {ruleset_id}")
    """
    rulesets = all_rulesets(token, owner, repo_name)
    main_ruleset = next((rs for rs in rulesets if rs["name"] == ruleset_name), None)
    return main_ruleset["id"] if main_ruleset else 0


def all_rulesets(token: str, owner: str, repo_name: str) -> Any:
    """Retrieve all rulesets defined for a repository.

    Args:
        token: GitHub API token with repository read permissions.
        owner: Repository owner — a GitHub username or organization name.
        repo_name: Repository name without the owner prefix.

    Returns:
        List of ruleset dictionaries. Each entry contains metadata such as
        ``id``, ``name``, ``target``, ``enforcement``, and ``rules``.
        Returns an empty list if no rulesets are defined.

    Raises:
        github.GithubException: If the API request fails.
    """
    return github_api_request(
        token, owner, repo_name, endpoint="rulesets", method="GET"
    )


def github_api_request(  # noqa: PLR0913
    token: str,
    owner: str,
    repo_name: str,
    endpoint: str,
    *,
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "GET",
    payload: dict[str, Any] | None = None,
) -> Any:
    """Make an authenticated GitHub REST API request for a repository.

    Constructs the full repository-scoped URL and delegates the HTTP call to
    PyGithub's internal requester, which handles authentication headers and
    JSON serialization automatically. This provides access to GitHub API
    endpoints that PyGithub does not expose through its high-level object model,
    such as repository rulesets.

    Args:
        token: GitHub API token for authentication.
        owner: Repository owner — a GitHub username or organization name.
        repo_name: Repository name without the owner prefix.
        endpoint: API path relative to the repository URL (e.g., ``"rulesets"``,
            ``"pages"``). Do not include a leading slash.
        method: HTTP method for the request. Defaults to ``"GET"``.
        payload: Optional dict to send as the JSON request body.
            Used with ``"POST"``, ``"PUT"``, and ``"PATCH"`` requests.

    Returns:
        Parsed JSON response as a ``dict`` or ``list``, depending on the endpoint.

    Raises:
        github.GithubException: If the API request fails (e.g., 4xx/5xx response).

    Note:
        This function relies on PyGithub's internal ``_requester`` object, which
        is not part of the public API and may change in future library versions.
    """
    logger.debug("GitHub API request: %s %s/%s/%s", method, owner, repo_name, endpoint)
    repo = repository(token, owner, repo_name)
    url = f"{repo.url}/{endpoint}"

    _headers, res = repo._requester.requestJsonAndCheck(  # noqa: SLF001
        method,
        url,
        input=payload,
    )
    logger.debug("GitHub API request successful: %s %s", method, endpoint)
    return res


def repository(token: str, owner: str, repo_name: str) -> "Repository":
    """Get an authenticated PyGithub ``Repository`` object.

    Creates a new PyGithub client authenticated with the given token and
    returns the corresponding repository object, which can be used for
    further GitHub API operations.

    Args:
        token: GitHub personal access token for authentication.
        owner: Repository owner — a GitHub username or organization name.
        repo_name: Repository name without the owner prefix.

    Returns:
        An authenticated ``github.Repository.Repository`` instance.

    Raises:
        github.UnknownObjectException: If the repository does not exist or
            the token does not have access to it.
        github.BadCredentialsException: If the token is invalid or expired.

    Examples:
        >>> repo = repository(token="ghp_...", owner="myorg", repo_name="myrepo")
        >>> print(repo.full_name)
        myorg/myrepo
    """
    auth = Token(token)
    github = Github(auth=auth)
    return github.get_repo(f"{owner}/{repo_name}")
