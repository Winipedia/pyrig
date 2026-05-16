"""module."""

from pytest_mock import MockerFixture

from pyrig.core.introspection.modules import reimport_module
from pyrig.core.introspection.packages import src_package_is_package
from pyrig.rig.configs.pyproject import PyprojectConfigFile as BasePyprojectConfigFile
from pyrig.rig.configs.pyrig import pyproject
from pyrig.rig.configs.pyrig.pyproject import PyprojectConfigFile


class TestPyprojectConfigFile:
    """Test class."""

    def test_make_python_version_classifiers(self) -> None:
        """Test method."""
        # no L for Base bc it would just use pyrigs Pyproject
        # and we want to assert differences between them
        base_classifiers = BasePyprojectConfigFile().make_python_version_classifiers()
        pyrig_classifiers = PyprojectConfigFile().make_python_version_classifiers()

        assert pyrig_classifiers != base_classifiers
        expected_extras = [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
        ]
        for classifier in expected_extras:
            assert classifier in pyrig_classifiers
            assert classifier not in base_classifiers

    def test__configs(self, mocker: MockerFixture) -> None:
        """Test method."""
        base_keywords = BasePyprojectConfigFile().configs()["project"]["keywords"]
        pyrig_keywords = PyprojectConfigFile().configs()["project"]["keywords"]
        assert base_keywords != pyrig_keywords
        expected_extras = [
            "project-setup",
            "automation",
        ]
        for keyword in expected_extras:
            assert keyword in pyrig_keywords
            assert keyword not in base_keywords

        mock_src_package_is_package = mocker.patch(
            src_package_is_package.__module__ + "." + src_package_is_package.__name__,
            return_value=False,
        )
        assert hasattr(pyproject, PyprojectConfigFile.__name__)
        module = reimport_module(pyproject)
        mock_src_package_is_package.assert_called_once()
        assert not hasattr(module, PyprojectConfigFile.__name__)

        # release the mock and reimport to reset state for other tests
        mock_src_package_is_package.stop()
        reimport_module(pyproject)
        assert hasattr(pyproject, PyprojectConfigFile.__name__)
