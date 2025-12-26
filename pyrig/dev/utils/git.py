"""GitHub repository API utilities and ruleset management.

This module provides utilities for interacting with the GitHub API, specifically
for repository rulesets and gitignore file handling. It uses the PyGithub library
for authentication and API calls.

GitHub rulesets are the modern mechanism for branch protection, offering more
flexibility and features than the legacy branch protection rules. This module
provides functions to create, update, and query rulesets programmatically.

Functions:
    get_rules_payload: Build a rules array for GitHub rulesets
    create_or_update_ruleset: Create or update a repository ruleset
    get_all_rulesets: Retrieve all rulesets for a repository
    get_repo: Get a PyGithub Repository object
    ruleset_exists: Check if a ruleset with a given name exists
    github_api_request: Make a generic GitHub API request
    get_github_repo_token: Retrieve GitHub token from environment or .env file
    path_is_in_gitignore: Check if a path matches gitignore patterns
    load_gitignore: Load gitignore file as a list of patterns

Module Attributes:
    DEFAULT_BRANCH (str): The default branch name used by pyrig ("main")
    DEFAULT_RULESET_NAME (str): The name of the default protection ruleset
    GITIGNORE_PATH (Path): Path to the .gitignore file

Examples:
    Create a ruleset with pull request requirements::

        >>> from pyrig.dev.utils.git import create_or_update_ruleset, get_rules_payload
        >>> rules = get_rules_payload(
        ...     pull_request={"required_approving_review_count": 1},
        ...     deletion={}
        ... )
        >>> create_or_update_ruleset(
        ...     token="ghp_...",
        ...     owner="myorg",
        ...     repo_name="myrepo",
        ...     name="main-protection",
        ...     target="branch",
        ...     enforcement="active",
        ...     rules=rules
        ... )

    Check if a path is gitignored::

        >>> from pyrig.dev.utils.git import path_is_in_gitignore
        >>> path_is_in_gitignore("__pycache__/")
        True
        >>> path_is_in_gitignore("src/main.py")
        False

See Also:
    pyrig.dev.cli.commands.protect_repo: High-level repository protection
    pyrig.dev.configs.branch_protection: Branch protection configuration
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

    Constructs a list of rule objects from the provided parameters. Each parameter
    corresponds to a specific GitHub ruleset rule type. Only non-None parameters
    are included in the output. Empty dictionaries create rules without parameters,
    while dictionaries with content create rules with those parameters.

    Args:
        creation: Restrict creation of matching refs to users with bypass permission.
            Pass an empty dict ({}) to enable without parameters.
        update: Restrict updates to matching refs to users with bypass permission.
            Pass an empty dict ({}) to enable without parameters.
        deletion: Restrict deletion of matching refs to users with bypass permission.
            Pass an empty dict ({}) to enable without parameters.
        required_linear_history: Prevent merge commits from being pushed to matching
            refs. Pass an empty dict ({}) to enable.
        merge_queue: Require merges to be performed via a merge queue. Parameters
            should specify merge queue configuration.
        required_deployments: Require successful deployments to specified environments
            before refs can be pushed. Parameters should include environment names.
        required_signatures: Require commits pushed to matching refs to have verified
            signatures. Pass an empty dict ({}) to enable.
        pull_request: Require all commits to be made to a non-target branch and
            submitted via a pull request. Parameters may include required approving
            review count, dismiss stale reviews, etc.
        required_status_checks: Require specified status checks to pass before the
            ref is updated. Parameters should include status check contexts.
        non_fast_forward: Prevent users with push access from force pushing to refs.
            Pass an empty dict ({}) to enable.
        commit_message_pattern: Enforce commit message patterns. Parameters should
            include pattern, operator, and optionally negate.
        commit_author_email_pattern: Enforce commit author email patterns. Parameters
            should include pattern, operator, and optionally negate.
        committer_email_pattern: Enforce committer email patterns. Parameters should
            include pattern, operator, and optionally negate.
        branch_name_pattern: Enforce branch name patterns. Parameters should include
            pattern, operator, and optionally negate.
        tag_name_pattern: Enforce tag name patterns. Parameters should include
            pattern, operator, and optionally negate.
        file_path_restriction: Prevent commits that include changes in specified
            file and folder paths. Parameters should include restricted file paths.
        max_file_path_length: Prevent commits with file paths exceeding the specified
            character limit. Parameters should include max_file_path_length value.
        file_extension_restriction: Prevent commits that include files with specified
            file extensions. Parameters should include restricted file extensions.
        max_file_size: Prevent commits with individual files exceeding the specified
            size limit. Parameters should include max_file_size value in bytes.
        workflows: Require all changes to a targeted branch to pass specified
            workflows. Parameters should include workflow file paths.
        code_scanning: Require specified code scanning tools to provide results
            before the reference is updated. Parameters should include tool names.
        copilot_code_review: Request GitHub Copilot code review for new pull requests
            automatically. Pass an empty dict ({}) to enable.

    Returns:
        A list of rule dictionaries, each with a "type" key and optionally a
        "parameters" key. The list only includes rules for which non-None arguments
        were provided. Empty list if no rules are specified.

    Examples:
        Create a simple deletion protection rule::

            >>> rules = get_rules_payload(deletion={})
            >>> print(rules)
            [{'type': 'deletion'}]

        Create a pull request rule with required reviews::

            >>> rules = get_rules_payload(
            ...     pull_request={"required_approving_review_count": 1}
            ... )
            >>> print(rules)
            [{'type': 'pull_request', 'parameters': {...}}]

        Create multiple rules::

            >>> rules = get_rules_payload(
            ...     deletion={},
            ...     creation={},
            ...     pull_request={"required_approving_review_count": 2}
            ... )
            >>> len(rules)
            3

    Note:
        The order of rules in the returned list matches the order of parameters
        in the function signature, not the order in which they were provided.
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

    Checks if a ruleset with the specified name already exists. If it does, the
    ruleset is updated with the new parameters. If it doesn't exist, a new ruleset
    is created. This function handles the idempotent creation/update pattern for
    repository rulesets.

    Args:
        token: GitHub API token with repository administration permissions. The
            token must have the `repo` scope or equivalent permissions to manage
            rulesets.
        owner: Repository owner username or organization name.
        repo_name: Repository name (without the owner prefix).
        **ruleset_params: Keyword arguments for the ruleset configuration as
            expected by the GitHub API. Must include a "name" key. Common parameters
            include:

            - name (str): Ruleset name (required)
            - target (str): Target type, typically "branch" or "tag"
            - enforcement (str): Enforcement level ("active", "evaluate", "disabled")
            - rules (list): List of rule objects (use get_rules_payload to build)
            - conditions (dict): Conditions for when the ruleset applies
            - bypass_actors (list): Users/teams who can bypass the ruleset

    Returns:
        The API response dictionary containing the created or updated ruleset data,
        including the ruleset ID, name, rules, and other configuration details.

    Raises:
        KeyError: If "name" is not present in ruleset_params.
        github.GithubException: If the API request fails due to authentication,
            permissions, or invalid parameters.

    Examples:
        Create a new ruleset::

            >>> from pyrig.dev.utils.git import create_or_update_ruleset
            >>> result = create_or_update_ruleset(
            ...     token="ghp_...",
            ...     owner="myorg",
            ...     repo_name="myrepo",
            ...     name="main-protection",
            ...     target="branch",
            ...     enforcement="active",
            ...     rules=[{"type": "deletion"}]
            ... )

        Update an existing ruleset::

            >>> result = create_or_update_ruleset(
            ...     token="ghp_...",
            ...     owner="myorg",
            ...     repo_name="myrepo",
            ...     name="main-protection",  # Same name = update
            ...     target="branch",
            ...     enforcement="active",
            ...     rules=[{"type": "deletion"}, {"type": "creation"}]
            ... )

    Note:
        This function logs informational messages about whether a ruleset is being
        created or updated. Debug logging includes the ruleset ID for updates.
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

    Fetches the complete list of repository rulesets from the GitHub API. This
    includes all rulesets regardless of their target (branch, tag) or enforcement
    level (active, evaluate, disabled).

    Args:
        token: GitHub API token with repository read permissions.
        owner: Repository owner username or organization name.
        repo_name: Repository name (without the owner prefix).

    Returns:
        A list of ruleset dictionaries from the GitHub API. Each dictionary contains
        ruleset metadata including id, name, target, enforcement, rules, and other
        configuration details. Returns an empty list if no rulesets are defined.

    Raises:
        github.GithubException: If the API request fails due to authentication,
            permissions, or network issues.

    Examples:
        Get all rulesets for a repository::

            >>> from pyrig.dev.utils.git import get_all_rulesets
            >>> rulesets = get_all_rulesets(
            ...     token="ghp_...",
            ...     owner="myorg",
            ...     repo_name="myrepo"
            ... )
            >>> for ruleset in rulesets:
            ...     print(f"{ruleset['name']}: {ruleset['enforcement']}")
    """
    return github_api_request(
        token, owner, repo_name, endpoint="rulesets", method="GET"
    )


def get_repo(token: str, owner: str, repo_name: str) -> Repository:
    """Get a PyGithub Repository object for API operations.

    Creates an authenticated PyGithub client and retrieves a Repository object
    for the specified repository. This object can be used for various GitHub API
    operations through the PyGithub library.

    Args:
        token: GitHub API token for authentication. The required permissions depend
            on the operations you intend to perform with the returned Repository
            object.
        owner: Repository owner username or organization name.
        repo_name: Repository name (without the owner prefix).

    Returns:
        A github.Repository.Repository object representing the specified repository.
        This object provides methods for interacting with the repository through
        the GitHub API.

    Raises:
        github.UnknownObjectException: If the repository doesn't exist or the token
            doesn't have permission to access it.
        github.BadCredentialsException: If the token is invalid or expired.

    Examples:
        Get a repository object::

            >>> from pyrig.dev.utils.git import get_repo
            >>> repo = get_repo(
            ...     token="ghp_...",
            ...     owner="myorg",
            ...     repo_name="myrepo"
            ... )
            >>> print(repo.full_name)
            'myorg/myrepo'
            >>> print(repo.default_branch)
            'main'
    """
    auth = Token(token)
    github = Github(auth=auth)
    return github.get_repo(f"{owner}/{repo_name}")


def ruleset_exists(token: str, owner: str, repo_name: str, ruleset_name: str) -> int:
    """Check if a ruleset with the given name exists in a repository.

    Searches through all rulesets in the repository to find one matching the
    specified name. This is useful for determining whether to create a new ruleset
    or update an existing one.

    Args:
        token: GitHub API token with repository read permissions.
        owner: Repository owner username or organization name.
        repo_name: Repository name (without the owner prefix).
        ruleset_name: Name of the ruleset to search for. The comparison is
            case-sensitive and must match exactly.

    Returns:
        The ruleset ID (a positive integer) if a ruleset with the given name exists,
        or 0 if no matching ruleset is found.

    Raises:
        github.GithubException: If the API request fails due to authentication,
            permissions, or network issues.

    Examples:
        Check if a ruleset exists::

            >>> from pyrig.dev.utils.git import ruleset_exists
            >>> ruleset_id = ruleset_exists(
            ...     token="ghp_...",
            ...     owner="myorg",
            ...     repo_name="myrepo",
            ...     ruleset_name="main-protection"
            ... )
            >>> if ruleset_id:
            ...     print(f"Ruleset exists with ID: {ruleset_id}")
            ... else:
            ...     print("Ruleset does not exist")

    Note:
        This function returns 0 (falsy) when the ruleset doesn't exist, making it
        convenient for boolean checks: `if ruleset_exists(...): ...`
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

    Performs an authenticated HTTP request to the GitHub API using PyGithub's
    internal requester. This function provides a low-level interface for API
    endpoints that may not be fully supported by PyGithub's high-level methods.

    Args:
        token: GitHub API token for authentication. Required permissions depend on
            the specific endpoint being accessed.
        owner: Repository owner username or organization name.
        repo_name: Repository name (without the owner prefix).
        endpoint: API endpoint path relative to the repository URL. For example,
            "rulesets", "pages", "actions/workflows". Do not include leading slash.
        method: HTTP method to use for the request. Defaults to "GET".
        payload: Optional dictionary to send as JSON in the request body. Used for
            POST, PUT, and PATCH requests. Ignored for GET and DELETE requests.

    Returns:
        The parsed JSON response from the GitHub API as a Python dictionary or list.
        The exact structure depends on the endpoint being called.

    Raises:
        github.GithubException: If the API request fails due to authentication,
            permissions, invalid parameters, or network issues.

    Examples:
        Get all rulesets::

            >>> from pyrig.dev.utils.git import github_api_request
            >>> rulesets = github_api_request(
            ...     token="ghp_...",
            ...     owner="myorg",
            ...     repo_name="myrepo",
            ...     endpoint="rulesets",
            ...     method="GET"
            ... )

        Create a new ruleset::

            >>> result = github_api_request(
            ...     token="ghp_...",
            ...     owner="myorg",
            ...     repo_name="myrepo",
            ...     endpoint="rulesets",
            ...     method="POST",
            ...     payload={"name": "my-ruleset", "target": "branch", ...}
            ... )

    Note:
        This function uses PyGithub's internal `_requester` object to make the
        request. It automatically includes the required GitHub API version header
        and handles JSON encoding/decoding.
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

    Searches for a GitHub API token in the following order of precedence:

    1. The `REPO_TOKEN` environment variable
    2. The `REPO_TOKEN` key in the project's `.env` file

    This priority order ensures CI/CD environments (which typically set environment
    variables) work seamlessly while allowing local development to use .env files
    for token storage.

    Returns:
        The GitHub API token as a string.

    Raises:
        ValueError: If the .env file doesn't exist when the REPO_TOKEN environment
            variable is not set, or if REPO_TOKEN is not found in the .env file.

    Examples:
        Get the token from environment or .env::

            >>> from pyrig.dev.utils.git import get_github_repo_token
            >>> token = get_github_repo_token()
            >>> print(token[:7])  # Print first 7 chars
            'ghp_...'

    Note:
        The token should have appropriate permissions for the intended operations:

        - `repo` scope: Full control of private repositories (includes rulesets)
        - `public_repo` scope: Access to public repositories only
        - `admin:repo_hook` scope: Repository webhook management

        For repository ruleset management, the `repo` scope is required.

    Security:
        Never commit tokens to version control. Always use environment variables
        or .env files (which should be gitignored). The .env file is automatically
        added to .gitignore by pyrig's initialization process.
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


def path_is_in_gitignore(relative_path: str | Path) -> bool:
    """Check if a path matches any pattern in the .gitignore file.

    Uses the pathspec library with gitwildmatch pattern matching (the same pattern
    matching used by Git) to determine if a path would be ignored by Git. Handles
    both files and directories, automatically appending a trailing slash to directory
    paths for proper pattern matching.

    Args:
        relative_path: Path to check, either as a string or Path object. Can be
            relative to the repository root or an absolute path (which will be
            converted to relative). Directories can be specified with or without
            a trailing slash.

    Returns:
        True if the path matches any pattern in .gitignore and would be ignored
        by Git. False if the path doesn't match any patterns or if .gitignore
        doesn't exist.

    Examples:
        Check if common paths are gitignored::

            >>> from pyrig.dev.utils.git import path_is_in_gitignore
            >>> path_is_in_gitignore("__pycache__")
            True
            >>> path_is_in_gitignore("__pycache__/")
            True
            >>> path_is_in_gitignore(".env")
            True
            >>> path_is_in_gitignore("src/main.py")
            False

        Check absolute paths::

            >>> from pathlib import Path
            >>> abs_path = Path.cwd() / "__pycache__"
            >>> path_is_in_gitignore(abs_path)
            True

    Note:
        This function automatically detects whether a path is a directory by
        checking if it has no suffix, ends with a path separator, or exists as
        a directory on the filesystem. Directories are matched with a trailing
        slash appended to ensure proper gitignore pattern matching.
    """
    if not GITIGNORE_PATH.exists():
        return False
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
        load_gitignore(),
    )

    return spec.match_file(as_posix)


def load_gitignore(path: Path = GITIGNORE_PATH) -> list[str]:
    """Load a gitignore file as a list of pattern strings.

    Reads the gitignore file and splits it into individual lines, preserving empty
    lines and comments. This format is suitable for use with pathspec.PathSpec.

    Args:
        path: Path to the gitignore file to load. Defaults to GITIGNORE_PATH
            (".gitignore" in the current directory).

    Returns:
        A list of strings, one per line in the gitignore file. Includes empty lines
        and comment lines (starting with #). The pathspec library handles filtering
        these appropriately.

    Raises:
        FileNotFoundError: If the specified gitignore file doesn't exist.
        UnicodeDecodeError: If the file contains invalid UTF-8 characters.

    Examples:
        Load the default .gitignore::

            >>> from pyrig.dev.utils.git import load_gitignore
            >>> patterns = load_gitignore()
            >>> print(patterns[:3])
            ['# Byte-compiled / optimized / DLL files', '__pycache__/', '*.py[cod]']

        Load a custom gitignore file::

            >>> from pathlib import Path
            >>> patterns = load_gitignore(Path("custom.gitignore"))

    Note:
        This function does not filter or process the patterns in any way. It simply
        reads the file and splits on newlines. Pattern interpretation is handled by
        the pathspec library when used with path_is_in_gitignore().
    """
    return path.read_text(encoding="utf-8").splitlines()
