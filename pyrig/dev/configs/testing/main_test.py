"""Has the test for main in src."""

from pathlib import Path

from pyrig import main
from pyrig.dev.configs.base.base import PythonPackageConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.module import to_path
from pyrig.src.testing.convention import make_test_obj_importpath_from_obj


class MainTestConfigFile(PythonPackageConfigFile):
    """Config file for test_main.py."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        test_module_path = to_path(
            make_test_obj_importpath_from_obj(main), is_package=False
        ).parent
        # replace pyrig with project name

        package_name = PyprojectConfigFile.get_package_name()
        test_module_path = Path(
            test_module_path.as_posix().replace("pyrig", package_name, 1)
        )
        return Path(test_module_path)

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        return "test_main"

    @classmethod
    def get_content_str(cls) -> str:
        """Get the config."""
        return '''"""test module."""

from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.os.os import run_subprocess


def test_main() -> None:
    """Test func for main."""
    project_name = PyprojectConfigFile.get_project_name()
    stdout = run_subprocess(["poetry", "run", project_name, "--help"]).stdout.decode(
        "utf-8"
    )
    assert project_name in stdout
'''

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the config is correct.

        Allow modifications to the test func.
        """
        return super().is_correct() or "def test_main" in cls.get_file_content()
