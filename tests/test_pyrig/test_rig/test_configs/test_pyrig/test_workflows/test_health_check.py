"""Test module."""

from pytest_mock import MockerFixture

from pyrig.core.introspection.modules import reimport_module
from pyrig.core.introspection.packages import src_package_is_package
from pyrig.rig.configs.pyrig.workflows import health_check
from pyrig.rig.configs.remote_version_control.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)


class TestHealthCheckWorkflowConfigFile:
    """Test class."""

    def test_step_run_tests(self, mocker: MockerFixture) -> None:
        """Test method."""
        step = HealthCheckWorkflowConfigFile.I.step_run_tests()
        assert step["env"]["REPO_TOKEN"] == "${{ secrets.REPO_TOKEN }}"  # noqa: S105

        step = HealthCheckWorkflowConfigFile.I.step_run_tests(
            step={"env": {"TEST": "test"}}
        )
        assert step["env"]["TEST"] == "test"
        assert step["env"]["REPO_TOKEN"] == "${{ secrets.REPO_TOKEN }}"  # noqa: S105

        mock_src_package_is_package = mocker.patch(
            src_package_is_package.__module__ + "." + src_package_is_package.__name__,
            return_value=False,
        )
        assert hasattr(health_check, HealthCheckWorkflowConfigFile.__name__)
        module = reimport_module(health_check)
        mock_src_package_is_package.assert_called_once()
        assert not hasattr(module, HealthCheckWorkflowConfigFile.__name__)
