"""module."""

from pyrig.rig.configs.pyproject import PyprojectConfigFile as BasePyprojectConfigFile
from pyrig.rig.configs.pyrig.pyproject import PyprojectConfigFile


class TestPyprojectConfigFile:
    """Test class."""

    def test_make_python_version_classifiers(self) -> None:
        """Test method."""
        # no L for Base bc it would just use pyrigs Pyproject
        # and we want to assert differences between them
        base_classifiers = BasePyprojectConfigFile.make_python_version_classifiers()
        pyrig_classifiers = PyprojectConfigFile.I.make_python_version_classifiers()

        assert pyrig_classifiers != base_classifiers
        expected_extras = [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
        ]
        for classifier in expected_extras:
            assert classifier in pyrig_classifiers
            assert classifier not in base_classifiers

    def test__configs(self) -> None:
        """Test method."""
        base_keywords = BasePyprojectConfigFile.configs()["project"]["keywords"]
        pyrig_keywords = PyprojectConfigFile.I.configs()["project"]["keywords"]
        assert base_keywords != pyrig_keywords
        expected_extras = [
            "project-setup",
            "automation",
        ]
        for keyword in expected_extras:
            assert keyword in pyrig_keywords
            assert keyword not in base_keywords
