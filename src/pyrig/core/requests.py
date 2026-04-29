"""Utility functions for making requests."""

import socket


def internet_is_available() -> bool:
    """Check internet connectivity by attempting a TCP connection.

    Attempts to open a TCP connection to Cloudflare's public HTTP server
    (1.1.1.1) on port 80 with a 2-second timeout. This provides a fast,
    reliable connectivity check without requiring DNS resolution or depending
    on any specific API endpoint.

    All connection errors are caught silently and result in ``False``, so
    this function never raises.

    Returns:
        bool: ``True`` if the connection succeeds, ``False`` otherwise.
    """
    try:
        with socket.create_connection(("1.1.1.1", 80), timeout=2):
            return True
    except OSError:
        return False
