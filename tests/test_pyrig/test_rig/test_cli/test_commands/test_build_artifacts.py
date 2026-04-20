"""Test module."""

from pytest_mock import MockerFixture

from pyrig.core.introspection.modules import callable_obj_import_path
from pyrig.rig.builders.base.builder import BuilderConfigFile
from pyrig.rig.cli.commands.build_artifacts import build_artifacts


def test_build_artifacts(mocker: MockerFixture) -> None:
    """Test function."""
    # mock validate_all_subclasses to avoid actually running builds
    mock_init = mocker.patch(
        callable_obj_import_path(BuilderConfigFile.validate_all_subclasses)
    )
    build_artifacts()
    mock_init.assert_called_once()
