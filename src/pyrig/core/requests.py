"""Network connectivity utilities.

Provides network availability checking for operations that require internet access.
Used by pyrig's resource fetching decorators to determine if remote resources
can be retrieved before falling back to local cached versions.

Functions:
    internet_is_available: Quick connectivity check via Cloudflare DNS.

Example:
    >>> from pyrig.src.requests import internet_is_available
    >>> if internet_is_available():
    ...     # Fetch remote resources
    ...     pass
"""

import socket


def internet_is_available() -> bool:
    """Check internet connectivity by attempting a socket connection.

    Tests connectivity by connecting to Cloudflare's public DNS server (1.1.1.1)
    on port 80. This provides a fast, reliable check without depending on
    specific API endpoints.

    Returns:
        True if connection succeeds, False otherwise.

    Note:
        Uses a 2-second timeout. Logs DEBUG on success, WARNING on failure.
        Does not raise exceptions; all connection errors return False.
    """
    try:
        with socket.create_connection(("1.1.1.1", 80), timeout=2):
            return True
    except OSError:
        return False
