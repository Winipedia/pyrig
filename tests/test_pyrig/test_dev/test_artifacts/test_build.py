"""Test module."""

from pytest_mock import MockFixture

from pyrig.dev.artifacts.build import build
from pyrig.dev.artifacts.builder.base.base import Builder
from pyrig.src.modules.module import make_obj_importpath


def test_build(mocker: MockFixture) -> None:
    """Test func for build."""
    # mock init_all_non_abstract_subclasses to avoid actually running builds
    mock_init = mocker.patch(
        make_obj_importpath(Builder.init_all_non_abstract_subclasses)
    )
    build()
    mock_init.assert_called_once()
