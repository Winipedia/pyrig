"""Resource fallback decorators for network operations.

Decorators that enable graceful fallback to local resource files when network
operations fail. Useful for fetching remote configuration with cached local copies
for offline operation.

Uses tenacity for exception handling and integrates with pyrig's resource system.
In pyrig development mode, automatically updates resource files with successful
fetch results to keep fallback content fresh.

Functions:
    return_resource_file_content_on_exceptions: Generic fallback decorator
    return_resource_content_on_fetch_error: HTTP request error fallback decorator

Examples:
    Fetch with fallback to resource file::

        >>> from pyrig.rig.utils.resources import (
        ...     return_resource_content_on_fetch_error
        ... )
        >>> @return_resource_content_on_fetch_error(resource_name="LATEST_VERSION")
        ... def fetch_latest_version() -> str:
        ...     response = requests.get("https://api.example.com/version")
        ...     response.raise_for_status()
        ...     return response.text

Note:
    In pyrig development mode, successful results are written back to resource
    files. Disable with overwrite_resource=False.
"""

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec

from requests import RequestException
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from pyrig import resources
from pyrig.rig.utils.packages import src_package_is_pyrig
from pyrig.src.resource import resource_path

logger = logging.getLogger(__name__)

P = ParamSpec("P")


def return_resource_file_content_on_exceptions(
    resource_name: str,
    exceptions: tuple[type[Exception], ...],
    *,
    overwrite_resource: bool = True,
    **tenacity_kwargs: Any,
) -> Callable[[Callable[P, str]], Callable[P, str]]:
    """Create a decorator that falls back to resource file content on exceptions.

    Wraps a function returning a string. If the function raises specified exceptions,
    returns resource file content instead. In pyrig development mode, successful
    results are written back to keep resource files fresh.

    Uses tenacity but does not retry - catches exception once and returns fallback.

    Args:
        resource_name: Resource file name (without path). E.g., "LATEST_VERSION"
            refers to `pyrig/resources/LATEST_VERSION`. Must exist.
        exceptions: Tuple of exception types that trigger fallback. Subclasses
            also trigger fallback.
        overwrite_resource: If True and in pyrig dev mode, write successful results
            back to resource file and stage in git. Defaults to True.
        **tenacity_kwargs: Additional tenacity retry decorator arguments. Note that
            stop and retry_error_callback are already configured.

    Returns:
        Decorator function for functions with signature `(*args, **kwargs) -> str`.

    Raises:
        FileNotFoundError: If resource file doesn't exist at decorator creation time.

    Examples:
        Fallback to resource file on network errors::

            >>> @return_resource_file_content_on_exceptions(
            ...     "GITIGNORE",
            ...     (requests.RequestException, TimeoutError)
            ... )
            ... def fetch_gitignore() -> str:
            ...     response = requests.get("https://example.com/.gitignore")
            ...     response.raise_for_status()
            ...     return response.text

    Note:
        Uses stop_after_attempt(1) - no actual retries.
    """
    path = resource_path(resource_name, resources)
    content = path.read_text(encoding="utf-8")

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
            result = decorated_func(*args, **kwargs)
            if src_package_is_pyrig() and overwrite_resource and result != content:
                path.write_text(result, encoding="utf-8")
                logger.info(
                    "Updated resource file: %s",
                    path,
                )
            return result

        return wrapper

    return decorator


def return_resource_content_on_fetch_error(
    resource_name: str,
    *,
    overwrite_resource: bool = True,
) -> Callable[[Callable[P, str]], Callable[P, str]]:
    """Create a decorator that falls back to resource file on HTTP request errors.

    Convenience wrapper around return_resource_file_content_on_exceptions for HTTP
    requests. Catches all requests.RequestException subclasses.

    Args:
        resource_name: Resource file name (without path) for fallback content.
            E.g., "LATEST_PYTHON_VERSION" refers to
            `pyrig/resources/LATEST_PYTHON_VERSION`.
        overwrite_resource: If True and in pyrig dev mode, write successful results
            back to resource file and stage in git. Defaults to True.

    Returns:
        Decorator function for HTTP request functions returning strings.

    Examples:
        Fetch with fallback to resource file::

            >>> @return_resource_content_on_fetch_error("LATEST_PYTHON_VERSION")
            ... def fetch_latest_python_version() -> str:
            ...     response = requests.get("https://endoflife.date/api/python.json")
            ...     response.raise_for_status()
            ...     return response.json()[0]["latest"]

    Note:
        Catches all RequestException subclasses (HTTPError, ConnectionError,
        Timeout, etc.). Successful fetches update resource file in pyrig dev mode.

    See Also:
        return_resource_file_content_on_exceptions: For custom exception types.
    """
    exceptions = (RequestException,)
    return return_resource_file_content_on_exceptions(
        resource_name,
        exceptions,
        overwrite_resource=overwrite_resource,
    )
