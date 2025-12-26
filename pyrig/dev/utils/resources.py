"""Resource fallback decorators for network operations.

This module provides decorators that enable graceful fallback to local resource
files when network operations fail. This is particularly useful for fetching
remote configuration files or data that should have a cached local copy.

The decorators use the tenacity library for retry logic and integrate with
pyrig's resource management system to automatically update resource files
when running in pyrig development mode.

Key Functions:
    - `return_resource_file_content_on_exceptions`: Generic fallback decorator
    - `return_resource_content_on_fetch_error`: Specialized for HTTP requests

Example:
    >>> from pyrig.dev.utils.resources import return_resource_content_on_fetch_error
    >>>
    >>> @return_resource_content_on_fetch_error(resource_name="LATEST_VERSION")
    ... def fetch_latest_version() -> str:
    ...     response = requests.get("https://api.example.com/version")
    ...     response.raise_for_status()
    ...     return response.text
    >>>
    >>> # If the request fails, returns content from resources/LATEST_VERSION
    >>> version = fetch_latest_version()
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

    This decorator wraps a function that returns a string. If the function raises
    any of the specified exceptions, the decorator returns the content of a
    resource file instead. When running in pyrig development mode, successful
    function results are written back to the resource file to keep it up-to-date.

    Args:
        resource_name: Name of the resource file (without path) in the resources
            directory. For example, "LATEST_VERSION" refers to
            `pyrig/resources/LATEST_VERSION`.
        exceptions: Tuple of exception types that should trigger the fallback.
            If the decorated function raises any of these, the resource file
            content is returned instead.
        overwrite_resource: If True and running in pyrig development mode,
            successful function results are written back to the resource file.
            This keeps the fallback content fresh. Defaults to True.
        **tenacity_kwargs: Additional keyword arguments passed to tenacity's
            `retry` decorator for advanced retry configuration.

    Returns:
        A decorator function that can be applied to functions returning strings.

    Note:
        The decorator uses tenacity with `stop_after_attempt(1)`, meaning it
        doesn't actually retry - it just catches the exception once and returns
        the fallback content.

    Example:
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

    This is a convenience wrapper around `return_resource_file_content_on_exceptions`
    specifically for HTTP requests. It catches all `requests.RequestException`
    subclasses (including `HTTPError`, `ConnectionError`, `Timeout`, etc.) and
    returns the resource file content as a fallback.

    Args:
        resource_name: Name of the resource file (without path) in the resources
            directory to use as fallback content.

    Returns:
        A decorator function for functions that make HTTP requests and return
        strings.

    Example:
        >>> from pyrig.dev.utils.resources import return_resource_content_on_fetch_error
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
        >>> # If the API is down, returns content from resources/LATEST_PYTHON_VERSION
        >>> version = fetch_latest_python_version()
        >>> print(version)
        '3.12.1'

    See Also:
        `return_resource_file_content_on_exceptions`: For custom exception handling.
    """
    exceptions = (RequestException,)
    return return_resource_file_content_on_exceptions(
        resource_name,
        exceptions,
    )
