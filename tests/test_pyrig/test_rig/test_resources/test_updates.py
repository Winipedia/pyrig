"""This test file contains tests that check if resources need updates.

It checks if pyrigs resource files like githubs gitignore
or the latest python version are up to date.
If not, the tests will fail prompting the developer to update the resource files.
"""

import json

import requests

from pyrig.core.resource import resource_path
from pyrig.rig import resources


def check_resource_file_is_up_to_date(
    url_text: str,
    resource_filename: str,
) -> None:
    """Check if a resource file is up to date with given text.

    Args:
        url_text: The text fetched from the URL to compare against the resource file.
        resource_filename: The name of the resource file to check (e.g., "GITIGNORE").
        If the resource file content does not match the url_text,
        it will be updated with the url_text and the test will fail,
        prompting the developer to update the resource file.
    """
    resource_file = resource_path(resource_filename, resources)
    resource_text = resource_file.read_text()

    if resource_text != url_text:
        resource_file.write_text(url_text)

    # using comparison again to allow pytest to show the diff in the test output
    assert resource_text == url_text, f"""Resource file {resource_filename} is outdated.
An update has been made to the resource file with the latest content from the URL.
Please review the changes to the resource file and commit the updated file."""


def test_gitignore(*, on_linux_and_latest_python_version_or_not_in_ci: bool) -> None:
    """Test if the github gitignore resource file is up to date."""
    if not on_linux_and_latest_python_version_or_not_in_ci:
        return
    url = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
    fetched_text = requests.get(url, timeout=(3, 10)).text

    check_resource_file_is_up_to_date(fetched_text, "GITIGNORE")


def test_latest_python_version() -> None:
    """Test if the latest python version resource file is up to date."""
    url = "https://endoflife.date/api/python.json"
    data: list[dict[str, str]] = json.loads(requests.get(url, timeout=(3, 10)).text)
    latest_version = data[0]["latest"]

    check_resource_file_is_up_to_date(latest_version, "LATEST_PYTHON_VERSION")


def test_mit_license_template(
    *, on_linux_and_latest_python_version_or_not_in_ci: bool
) -> None:
    """Test if the MIT license template resource file is up to date."""
    # this url has a rate limit so we only test if we are on linux
    # and the current python version is the latest one to
    # avoid hitting the rate limit in CI due to the matrix testing
    if not on_linux_and_latest_python_version_or_not_in_ci:
        return
    url = "https://api.github.com/licenses/mit"
    data = json.loads(requests.get(url, timeout=(3, 10)).text)
    assert "body" in data, json.dumps(data, indent=4)
    mit_license: str = data["body"]
    check_resource_file_is_up_to_date(mit_license, "MIT_LICENSE")


def test_contributor_covenant_code_of_conduct(
    *, on_linux_and_latest_python_version_or_not_in_ci: bool
) -> None:
    """Test if the Contributor Covenant Code of Conduct resource file is up to date."""
    # this url has a rate limit so we only test if we are on linux
    # and the current python version is the latest one to
    # avoid hitting the rate limit in CI due to the matrix testing
    if not on_linux_and_latest_python_version_or_not_in_ci:
        return

    url = (
        "https://raw.githubusercontent.com/github/MVG/main/org-docs/CODE-OF-CONDUCT.md"
    )
    fetched_text = requests.get(url, timeout=(3, 10)).text

    check_resource_file_is_up_to_date(
        fetched_text, "CONTRIBUTOR_COVENANT_CODE_OF_CONDUCT"
    )
