"""Utilities for network operations."""

from typing import Any

import requests
from requests import Response


def get_json(url: str, *args: Any, **kwargs: Any) -> Any:
    """Make a GET request to `url` and return the response body parsed as JSON."""
    return get(url, *args, **kwargs).json()


def get_text(url: str, *args: Any, **kwargs: Any) -> str:
    """Make a GET request to `url` and return the response body as text."""
    return get(url, *args, **kwargs).text


def get(url: str, *args: Any, **kwargs: Any) -> Response:
    """Make a GET request with a default connect/read timeout.

    A ``timeout`` kwarg overrides the default.

    Args:
        url: URL to request.
        *args: Positional arguments forwarded to ``requests.get``.
        **kwargs: Keyword arguments forwarded to ``requests.get``.

    Returns:
        The HTTP response.
    """
    timeout = kwargs.pop("timeout", (3, 10))
    return requests.get(url, *args, timeout=timeout, **kwargs)
