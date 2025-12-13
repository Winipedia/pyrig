"""Decorators for various purposes.

This module provides decorators for various purposes, including:
    - Retry and Exponential Handling
"""

from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec

from requests import RequestException
from tenacity import retry, retry_if_exception_type, stop_after_attempt

import pyrig
from pyrig import resources
from pyrig.src.git.git import git_add_file
from pyrig.src.modules.package import get_pkg_name_from_cwd
from pyrig.src.resource import get_resource_path

P = ParamSpec("P")


def return_resource_file_content_on_exceptions(
    resource_name: str,
    exceptions: tuple[type[Exception], ...],
    *,
    overwrite_resource: bool = True,
    **tenacity_kwargs: Any,
) -> Callable[[Callable[P, str]], Callable[P, str]]:
    """Return content of a resource file if func raises specific exceptions.

    post_process: Optional function that takes the result and returns a new value.
    overwrite_resource: If True, write the result to the resource file.
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
            if (
                get_pkg_name_from_cwd() == pyrig.__name__
                and overwrite_resource
                and result != content
            ):
                resource_path.write_text(result, encoding="utf-8")
                git_add_file(resource_path)
            return result

        return wrapper

    return decorator


def return_resource_content_on_fetch_error(
    resource_name: str,
) -> Callable[[Callable[P, str]], Callable[P, str]]:
    """Return content of a resource file if func raises a requests.HTTPError."""
    exceptions = (RequestException,)
    return return_resource_file_content_on_exceptions(
        resource_name,
        exceptions,
    )
