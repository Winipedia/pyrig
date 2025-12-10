"""Test module."""

from pytest_mock import MockFixture

from pyrig.dev.builders.base.base import Builder
from pyrig.dev.cli.commands.build_artifacts import build_artifacts
from pyrig.src.modules.module import make_obj_importpath


def test_build_artifacts(mocker: MockFixture) -> None:
    """Test func for build."""
    # mock init_all_non_abstract_subclasses to avoid actually running builds
    mock_init = mocker.patch(
        make_obj_importpath(Builder.init_all_non_abstract_subclasses)
    )
    build_artifacts()
    mock_init.assert_called_once()
