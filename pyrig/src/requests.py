"""Some simple network utilities."""

import socket


def internet_is_available() -> bool:
    """Check if internet is available."""
    try:
        socket.create_connection(("www.google.com", 80))
    except OSError:
        return False
    else:
        return True
