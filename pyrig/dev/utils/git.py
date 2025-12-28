"""GitHub repository API utilities and ruleset management.

Utilities for interacting with the GitHub API, specifically for repository rulesets
and gitignore file handling. Uses PyGithub for authentication and API calls.

GitHub rulesets are the modern mechanism for branch protection, offering more
flexibility than legacy branch protection rules.

Functions:
    get_rules_payload: Build a rules array for GitHub rulesets
    create_or_update_ruleset: Create or update a repository ruleset
    get_all_rulesets: Retrieve all rulesets for a repository
    get_repo: Get a PyGithub Repository object
    ruleset_exists: Check if a ruleset with a given name exists
    github_api_request: Make a generic GitHub API request
    get_github_repo_token: Retrieve GitHub token from environment or .env
    path_is_in_gitignore_lines: Check if a path matches gitignore patterns
    load_gitignore: Load gitignore file as a list of patterns

Module Attributes:
    DEFAULT_BRANCH (str): Default branch name ("main")
    DEFAULT_RULESET_NAME (str): Default protection ruleset name
    GITIGNORE_PATH (Path): Path to .gitignore file

Examples:
    Create a ruleset with pull request requirements::

        >>> from pyrig.dev.utils.git import create_or_update_ruleset, get_rules_payload
        >>> rules = get_rules_payload(
        ...     pull_request={"required_approving_review_count": 1},
        ...     deletion={}
        ... )
        >>> create_or_update_ruleset(
        ...     token="ghp_...", owner="myorg", repo_name="myrepo",
        ...     name="main-protection", target="branch",
        ...     enforcement="active", rules=rules
        ... )

See Also:
    pyrig.dev.cli.commands.protect_repo: High-level repository protection
"""

import logging
import os
from pathlib import Path
from typing import Any, Literal

import pathspec
from dotenv import dotenv_values
from github import Github
from github.Auth import Token
from github.Repository import Repository

logger = logging.getLogger(__name__)

DEFAULT_BRANCH = "main"

DEFAULT_RULESET_NAME = f"{DEFAULT_BRANCH}-protection"

GITIGNORE_PATH = Path(".gitignore")


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
    """Build a rules array for a GitHub repository ruleset.

    Constructs a list of rule objects from provided parameters. Each parameter
    corresponds to a GitHub ruleset rule type. Only non-None parameters are included.
    Empty dicts create rules without parameters; dicts with content include those
    parameters.

    Args:
        creation: Restrict ref creation to bypass users. Pass {} to enable.
        update: Restrict ref updates to bypass users. Pass {} to enable.
        deletion: Restrict ref deletion to bypass users. Pass {} to enable.
        required_linear_history: Prevent merge commits. Pass {} to enable.
        merge_queue: Require merge queue. Parameters specify configuration.
        required_deployments: Require deployments. Parameters include environments.
        required_signatures: Require verified signatures. Pass {} to enable.
        pull_request: Require pull requests. Parameters may include review count,
            dismiss stale reviews, etc.
        required_status_checks: Require status checks. Parameters include contexts.
        non_fast_forward: Prevent force pushing. Pass {} to enable.
        commit_message_pattern: Enforce commit message patterns. Parameters:
            pattern, operator, optionally negate.
        commit_author_email_pattern: Enforce author email patterns. Parameters:
            pattern, operator, optionally negate.
        committer_email_pattern: Enforce committer email patterns. Parameters:
            pattern, operator, optionally negate.
        branch_name_pattern: Enforce branch name patterns. Parameters: pattern,
            operator, optionally negate.
        tag_name_pattern: Enforce tag name patterns. Parameters: pattern,
            operator, optionally negate.
        file_path_restriction: Prevent commits with changes in specified paths.
            Parameters include restricted paths.
        max_file_path_length: Prevent long file paths. Parameters include
            max_file_path_length value.
        file_extension_restriction: Prevent specified file extensions.
            Parameters include restricted extensions.
        max_file_size: Prevent large files. Parameters include max_file_size
            in bytes.
        workflows: Require workflows to pass. Parameters include workflow paths.
        code_scanning: Require code scanning. Parameters include tool names.
        copilot_code_review: Request Copilot code review. Pass {} to enable.

    Returns:
        List of rule dictionaries with "type" and optionally "parameters" keys.
        Empty list if no rules specified.

    Examples:
        Create a simple deletion protection rule::

            >>> rules = get_rules_payload(deletion={})
            [{'type': 'deletion'}]

        Create multiple rules::

            >>> rules = get_rules_payload(
            ...     deletion={},
            ...     pull_request={"required_approving_review_count": 2}
            ... )
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

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    _headers, res = repo._requester.requestJsonAndCheck(  # noqa: SLF001
        method,
        url,
        headers=headers,
        input=payload,
    )
    logger.debug("GitHub API request successful: %s %s", method, endpoint)
    return res


def get_github_repo_token() -> str:
    """Retrieve the GitHub repository token for API authentication.

    Searches for REPO_TOKEN in order: environment variable, then .env file.

    Returns:
        GitHub API token string.

    Raises:
        ValueError: If .env doesn't exist when REPO_TOKEN not in environment,
            or if REPO_TOKEN not found in .env.

    Examples:
        Get the token::

            >>> token = get_github_repo_token()
            >>> print(token[:7])
            'ghp_...'

    Note:
        For ruleset management, token needs `repo` scope.

    Security:
        Never commit tokens. Use environment variables or .env (gitignored).
    """
    # try os env first
    token = os.getenv("REPO_TOKEN")
    if token:
        logger.debug("Using REPO_TOKEN from environment variable")
        return token

    # try .env next
    dotenv_path = Path(".env")
    if not dotenv_path.exists():
        msg = f"Expected {dotenv_path} to exist"
        raise ValueError(msg)
    dotenv = dotenv_values(dotenv_path)
    token = dotenv.get("REPO_TOKEN")
    if token:
        logger.debug("Using REPO_TOKEN from .env file")
        return token

    msg = f"Expected REPO_TOKEN in {dotenv_path}"
    raise ValueError(msg)


def path_is_in_gitignore_lines(
    gitignore_lines: list[str], relative_path: str | Path
) -> bool:
    """Check if a path matches any pattern in a list of gitignore lines.

    Args:
        gitignore_lines: List of gitignore pattern strings.
        relative_path: Path to check (string or Path). Absolute paths converted
            to relative. Directories can have optional trailing slash.

    Returns:
        True if path matches any pattern and would be ignored by Git.

    See Also:
        load_gitignore: Load patterns from .gitignore file.
    """
    as_path = Path(relative_path)
    if as_path.is_absolute():
        as_path = as_path.relative_to(Path.cwd())
    is_dir = (
        bool(as_path.suffix == "") or as_path.is_dir() or str(as_path).endswith(os.sep)
    )
    is_dir = is_dir and not as_path.is_file()

    as_posix = as_path.as_posix()
    if is_dir and not as_posix.endswith("/"):
        as_posix += "/"

    spec = pathspec.PathSpec.from_lines(
        "gitwildmatch",
        gitignore_lines,
    )

    return spec.match_file(as_posix)


def load_gitignore(path: Path = GITIGNORE_PATH) -> list[str]:
    """Load a gitignore file as a list of pattern strings.

    Reads gitignore file and splits into lines. Preserves empty lines and comments
    for use with pathspec.PathSpec.

    Args:
        path: Path to gitignore file. Defaults to GITIGNORE_PATH (".gitignore").

    Returns:
        List of strings, one per line. Includes empty lines and comments.

    Raises:
        FileNotFoundError: If gitignore file doesn't exist.
        UnicodeDecodeError: If file contains invalid UTF-8.

    Examples:
        Load the default .gitignore::

            >>> patterns = load_gitignore()
            >>> print(patterns[:3])
            ['# Byte-compiled / optimized / DLL files', '__pycache__/', '*.py[cod]']

    See Also:
        path_is_in_gitignore_lines: Check if path matches patterns

    Note:
        Does not filter or process patterns. Pattern interpretation handled by
        pathspec library.
    """
    return path.read_text(encoding="utf-8").splitlines()
