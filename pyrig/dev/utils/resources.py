"""Resource fallback decorators for network operations.

This module provides decorators that enable graceful fallback to local resource
files when network operations fail. This is particularly useful for fetching
remote configuration files or data that should have a cached local copy for
offline operation or when external services are unavailable.

The decorators use the tenacity library for exception handling and integrate with
pyrig's resource management system. When running in pyrig development mode, they
automatically update resource files with successful fetch results, keeping the
fallback content fresh.

Functions:
    return_resource_file_content_on_exceptions: Generic fallback decorator for
        any exception types
    return_resource_content_on_fetch_error: Specialized decorator for HTTP
        request errors (requests.RequestException)

Examples:
    Fetch with fallback to resource file::

        >>> from pyrig.dev.utils.resources import (
        ...     return_resource_content_on_fetch_error
        ... )
        >>> import requests
        >>>
        >>> @return_resource_content_on_fetch_error(resource_name="LATEST_VERSION")
        ... def fetch_latest_version() -> str:
        ...     response = requests.get("https://api.example.com/version")
        ...     response.raise_for_status()
        ...     return response.text
        >>>
        >>> # If the request fails, returns content from resources/LATEST_VERSION
        >>> version = fetch_latest_version()
        >>> print(version)
        '1.2.3'

    Custom exception handling::

        >>> from pyrig.dev.utils.resources import (
        ...     return_resource_file_content_on_exceptions
        ... )
        >>>
        >>> @return_resource_file_content_on_exceptions(
        ...     resource_name="CONFIG",
        ...     exceptions=(TimeoutError, ConnectionError),
        ...     overwrite_resource=False
        ... )
        ... def fetch_config() -> str:
        ...     # Fetch configuration from remote source
        ...     return remote_config

Note:
    When running in pyrig development mode (detected via src_pkg_is_pyrig()),
    successful function results are automatically written back to the resource
    file to keep fallback content up-to-date. This behavior can be disabled
    by setting overwrite_resource=False.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec

from requests import RequestException
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from pyrig import resources
from pyrig.dev.utils.packages import src_pkg_is_pyrig
from pyrig.src.git import git_add_file
from pyrig.src.resource import get_resource_path

P = ParamSpec("P")


def return_resource_file_content_on_exceptions(
    resource_name: str,
    exceptions: tuple[type[Exception], ...],
    *,
    overwrite_resource: bool = True,
    **tenacity_kwargs: Any,
) -> Callable[[Callable[P, str]], Callable[P, str]]:
    """Create a decorator that falls back to resource file content on exceptions.

    Wraps a function that returns a string. If the function raises any of the
    specified exceptions, the decorator returns the content of a resource file
    instead. When running in pyrig development mode, successful function results
    are automatically written back to the resource file to keep it up-to-date.

    The decorator uses tenacity for exception handling but does not retry - it
    catches the exception once and immediately returns the fallback content.

    Args:
        resource_name: Name of the resource file (without path or directory prefix)
            in the resources directory. For example, "LATEST_VERSION" refers to
            `pyrig/resources/LATEST_VERSION`. The file must exist.
        exceptions: Tuple of exception types that should trigger the fallback to
            resource file content. If the decorated function raises any of these
            exception types (or their subclasses), the resource file content is
            returned instead of propagating the exception.
        overwrite_resource: If True and running in pyrig development mode (detected
            via src_pkg_is_pyrig()), successful function results are written back
            to the resource file and staged in git. This keeps the fallback content
            fresh. Defaults to True. Set to False to prevent resource file updates.
        **tenacity_kwargs: Additional keyword arguments passed to tenacity's retry
            decorator for advanced configuration.
            Note that stop and retry_error_callback are already configured
            and will be overridden if provided.

    Returns:
        A decorator function that can be applied to functions with signature
        `(*args: P.args, **kwargs: P.kwargs) -> str`. The decorated function will
        have the same signature but with fallback behavior added.

    Examples:
        Fallback to resource file on network errors::

            >>> from pyrig.dev.utils.resources import (
            ...     return_resource_file_content_on_exceptions
            ... )
            >>> import requests
            >>>
            >>> @return_resource_file_content_on_exceptions(
            ...     "GITHUB_GITIGNORE",
            ...     (requests.RequestException, TimeoutError),
            ...     overwrite_resource=True
            ... )
            ... def fetch_gitignore() -> str:
            ...     response = requests.get("https://example.com/.gitignore")
            ...     response.raise_for_status()
            ...     return response.text
            >>>
            >>> # If request fails, returns content from resources/GITHUB_GITIGNORE
            >>> content = fetch_gitignore()

        Disable resource file updates::

            >>> @return_resource_file_content_on_exceptions(
            ...     "CONFIG",
            ...     (IOError,),
            ...     overwrite_resource=False
            ... )
            ... def fetch_config() -> str:
            ...     return read_remote_config()

    Note:
        The decorator strips whitespace from both the resource file content and
        the function result using .strip(). This ensures consistent formatting
        regardless of trailing newlines in the resource file.

        The decorator uses tenacity with stop_after_attempt(1), meaning it doesn't
        actually retry the operation - it just catches the exception once and
        returns the fallback content.
    """
    resource_path = get_resource_path(resource_name, resources)
    content = resource_path.read_text(encoding="utf-8").strip()

    def decorator(func: Callable[P, str]) -> Callable[P, str]:
        tenacity_decorator = retry(
            retry=retry_if_exception_type(exception_types=exceptions),
            stop=stop_after_attempt(
                max_attempt_number=1
            ),  # no retries, just catch once
            retry_error_callback=lambda _state: content,
            reraise=False,
            **tenacity_kwargs,
        )

        # Apply tenacity decorator to the function once
        decorated_func = tenacity_decorator(func)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> str:
            result = decorated_func(*args, **kwargs).strip()
            if src_pkg_is_pyrig() and overwrite_resource and result != content:
                resource_path.write_text(result, encoding="utf-8")
                git_add_file(resource_path)
            return result

        return wrapper

    return decorator


def return_resource_content_on_fetch_error(
    resource_name: str,
) -> Callable[[Callable[P, str]], Callable[P, str]]:
    """Create a decorator that falls back to resource file on HTTP request errors.

    Convenience wrapper around return_resource_file_content_on_exceptions specifically
    for HTTP requests using the requests library. Catches all requests.RequestException
    subclasses and returns the resource file content as a fallback.

    This decorator is equivalent to calling return_resource_file_content_on_exceptions
    with exceptions=(RequestException,), but provides a more concise and semantically
    clear interface for the common case of HTTP request fallbacks.

    Args:
        resource_name: Name of the resource file (without path or directory prefix)
            in the resources directory to use as fallback content. For example,
            "LATEST_PYTHON_VERSION" refers to `pyrig/resources/LATEST_PYTHON_VERSION`.

    Returns:
        A decorator function for functions that make HTTP requests and return strings.
        The decorated function will fall back to the resource file content if any
        requests.RequestException is raised.

    Examples:
        Fetch with fallback to resource file::

            >>> from pyrig.dev.utils.resources import (
            ...     return_resource_content_on_fetch_error
            ... )
            >>> import requests
            >>>
            >>> @return_resource_content_on_fetch_error(
            ...     resource_name="LATEST_PYTHON_VERSION"
            ... )
            ... def fetch_latest_python_version() -> str:
            ...     response = requests.get("https://endoflife.date/api/python.json")
            ...     response.raise_for_status()
            ...     data = response.json()
            ...     return data[0]["latest"]
            >>>
            >>> # If the API is down, returns content from resource file
            >>> version = fetch_latest_python_version()
            >>> print(version)
            '3.12.1'

        Use in pyrig configuration files::

            >>> @return_resource_content_on_fetch_error("GITIGNORE")
            ... def fetch_github_gitignore() -> str:
            ...     url = "https://raw.githubusercontent.com/github/gitignore/..."
            ...     response = requests.get(url, timeout=10)
            ...     response.raise_for_status()
            ...     return response.text

    Note:
        This decorator catches all requests.RequestException subclasses, including:

        - HTTPError: HTTP error responses (4xx, 5xx status codes)
        - ConnectionError: Network connection failures
        - Timeout: Request timeout
        - TooManyRedirects: Exceeded maximum redirects
        - URLRequired: Invalid URL
        - And all other requests exceptions

        The overwrite_resource parameter defaults to True, meaning successful
        fetches will update the resource file when running in pyrig development mode.

    See Also:
        return_resource_file_content_on_exceptions: For custom exception handling
            with different exception types or configuration.
    """
    exceptions = (RequestException,)
    return return_resource_file_content_on_exceptions(
        resource_name,
        exceptions,
    )
