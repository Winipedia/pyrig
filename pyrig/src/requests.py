"""Some simple network utilities."""

import logging
import socket

logger = logging.getLogger(__name__)


def internet_is_available() -> bool:
    """Check if internet is available."""
    try:
        with socket.create_connection(("1.1.1.1", 80), timeout=2):
            logger.info("Internet is available")
            return True
    except OSError:
        logger.warning("Internet is not available")
        return False
