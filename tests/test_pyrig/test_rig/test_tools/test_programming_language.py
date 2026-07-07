"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig.rig.tools.testers.project import ProjectTester


class TestProgrammingLanguage:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            ProgrammingLanguage().image_url()
            == "https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert ProgrammingLanguage.I.link_url() == "https://www.python.org"

    def test_version_control_ignore_paths(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().version_control_ignore_paths() == ("__pycache__/",)

    def test_standard_init_content(self) -> None:
        """Test method."""
        assert isinstance(ProgrammingLanguage().standard_init_content(), str)

    def test_no_bytecode_env_var(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().no_bytecode_env_var() == "PYTHONDONTWRITEBYTECODE"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().dev_dependencies() == ()

    def test_name(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().name() == "python"

    def test_group(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().group() == Group.PROJECT_INFO

    def test_make_init_files(
        self,
        tmp_project_root_path: Path,
        tmp_package_root_path: tuple[Path, ModuleType],
    ) -> None:
        """Test function."""
        with chdir(tmp_project_root_path):
            docs = Path("docs")
            docs.mkdir()
            ProjectTester.I.package_root().mkdir()
            package_root_path, _ = tmp_package_root_path
            root_init = package_root_path / "__init__.py"
            # assert ends with empty line
            root_init.unlink()
            assert not root_init.exists()

            assert set(ProgrammingLanguage.I.namespace_package_paths()) == {
                PackageManager.I.package_root(),
                ProjectTester.I.package_root(),
            }
            ProgrammingLanguage.I.make_init_files()
            assert list(ProgrammingLanguage.I.namespace_package_paths()) == []
            content = root_init.read_text()
            assert content.endswith('"""\n')
            assert not (docs / "__init__.py").exists()

    def test_namespace_package_paths(
        self,
        tmp_project_root_path: Path,
        tmp_package_root_path: tuple[Path, ModuleType],
        create_source_package: Callable[[Path], ModuleType],
    ) -> None:
        """Test function."""
        package_root_path, _ = tmp_package_root_path

        with chdir(tmp_project_root_path):
            Path("docs").mkdir()
            assert list(ProgrammingLanguage.I.namespace_package_paths()) == []

            create_source_package(Path("package"))

            namespace_package = package_root_path / "namespace_package"
            namespace_package.mkdir()
            pycache = namespace_package / "__pycache__"
            pycache.mkdir()
            assert pycache.is_dir()
            assert list(ProgrammingLanguage.I.namespace_package_paths()) == [
                namespace_package.relative_to(Path.cwd())
            ]
