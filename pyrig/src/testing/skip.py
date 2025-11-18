"""Has utils towards skipping tests."""

import functools

import pytest

from pyrig.src.git.github.github import running_in_github_actions

skip_fixture_test: pytest.MarkDecorator = functools.partial(
    pytest.mark.skip,
    reason="Fixtures are not testable bc they cannot be called directly.",
)()


skip_in_github_actions: pytest.MarkDecorator = functools.partial(
    pytest.mark.skipif,
    running_in_github_actions(),
    reason="Test cannot run in GitHub action.",
)()
