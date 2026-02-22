"""Pytest skip markers for conditional test execution.

Convenience skip markers for pytest testing. Simplifies common patterns for
conditional test skipping based on environment (CI, network availability) or
test type (fixture tests).

All markers are partial applications of pytest.mark.skip or pytest.mark.skipif
with pre-configured conditions.

Attributes:
    skip_if_no_internet: Skip marker for tests that require internet connection.

Examples:
    Skip tests in GitHub Actions:

        >>> from pyrig.rig.utils.testing import skip_if_no_internet
        >>> @skip_if_no_internet
        ... def test_network_required():
        ...     assert internet_is_available()

See Also:
    pytest.mark.skip: Underlying pytest skip marker.
    pytest.mark.skipif: Underlying pytest conditional skip marker.
"""

import functools

import pytest

from pyrig.src.requests import internet_is_available

skip_if_no_internet: pytest.MarkDecorator = functools.partial(
    pytest.mark.skipif,
    not internet_is_available(),
    reason="Test requires internet connection.",
)()
"""Skip marker for tests that require an internet connection.

Automatically skips tests when no internet connectivity is detected. Uses a quick
socket connection check to Cloudflare DNS (1.1.1.1) to determine availability.

Examples:
    Skip a test requiring network access:

        >>> @skip_if_no_internet
        ... def test_api_integration():
        ...     response = api_client.fetch_data()
        ...     assert response.status_code == 200

See Also:
    pyrig.src.requests.internet_is_available: Underlying connectivity check
"""
