"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig.rig.tools.testing.project import ProjectTester


class TestProgrammingLanguage:
    """Test class."""

    def test_dev_dependencies(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().dev_dependencies() == ()

    def test_group(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().group() == Group.PROJECT_INFO

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            ProgrammingLanguage().image_url()
            == "https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert ProgrammingLanguage.I.link_url() == "https://www.python.org"

    def test_make_init_files(
        self,
        tmp_path: Path,
    ) -> None:
        """Test function."""
        with chdir(tmp_path):
            docs = Path("docs")
            docs.mkdir()
            ProjectTester.I.package_root().mkdir(parents=True)
            package_root_path = PackageManager.I.package_root()
            package_root_path.mkdir(parents=True)
            root_init = package_root_path / "__init__.py"
            # assert ends with empty line
            root_init.touch()
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

    def test_name(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().name() == "python"

    def test_namespace_package_paths(
        self,
        tmp_path: Path,
    ) -> None:
        """Test function."""
        with chdir(tmp_path):
            package_root_path = PackageManager.I.package_root()
            package_root_path.mkdir(parents=True)
            ProjectTester.I.package_root().mkdir(parents=True)
            (package_root_path / "__init__.py").write_text("")
            (ProjectTester.I.package_root() / "__init__.py").write_text("")
            Path("docs").mkdir()
            assert list(ProgrammingLanguage.I.namespace_package_paths()) == []

            source_package = PackageManager.I.package_root() / "package"
            source_package.mkdir()
            (source_package / "__init__.py").write_text("")

            namespace_package = package_root_path / "namespace_package"
            namespace_package.mkdir()
            pycache = namespace_package / "__pycache__"
            pycache.mkdir()
            assert pycache.is_dir()
            assert list(ProgrammingLanguage.I.namespace_package_paths()) == [
                namespace_package,
            ]

    def test_remove_pycache(
        self,
        tmp_path: Path,
    ) -> None:
        """Test function."""
        with chdir(tmp_path):
            package_root_path = PackageManager.I.package_root()
            package_root_path.mkdir(parents=True)
            pycache_path = package_root_path / "__pycache__"
            module_path = package_root_path / "module.py"
            module_path.touch()
            pycache_path.mkdir()
            assert pycache_path.exists()
            ProgrammingLanguage.I.remove_pycache()
            assert not pycache_path.exists()
            assert module_path.exists()

            tests_path = Path("tests")
            tests_path.mkdir()
            pycache_tests_path = tests_path / "__pycache__"
            pycache_tests_path.mkdir()
            assert pycache_tests_path.exists()
            ProgrammingLanguage.I.remove_pycache()
            assert not pycache_tests_path.exists()

            # Test with no __pycache__ directories
            ProgrammingLanguage.I.remove_pycache()
            assert not pycache_path.exists()
            assert not pycache_tests_path.exists()

            # check with nested __pycache__ directories
            nested_path = package_root_path / "nested"
            nested_path.mkdir()
            nested_pycache_path = nested_path / "__pycache__"
            nested_pycache_path.mkdir()
            assert nested_pycache_path.exists()
            deep_nested_pycache_path = (
                package_root_path / "deep" / "nested" / "__pycache__"
            )
            deep_nested_pycache_path.mkdir(parents=True)
            assert deep_nested_pycache_path.exists()
            double_nested_pycache_path = (
                package_root_path
                / "deep"
                / "__pycache__"
                / "__pycache__"
                / "__pycache__"
            )
            double_nested_pycache_path.mkdir(parents=True)
            assert double_nested_pycache_path.exists()
            # A file named __pycache__ should be matched by rglob but skipped
            # because it is not a directory.
            pycache_file = package_root_path / "file_only" / "__pycache__"
            pycache_file.parent.mkdir()
            pycache_file.touch()
            assert pycache_file.is_file()
            ProgrammingLanguage.I.remove_pycache()
            assert not nested_pycache_path.exists()
            assert not deep_nested_pycache_path.exists()
            assert pycache_file.is_file()

    def test_standard_init_content(self) -> None:
        """Test method."""
        assert isinstance(ProgrammingLanguage().standard_init_content(), str)

    def test_version_control_ignore_patterns(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().version_control_ignore_patterns() == (
            "__pycache__/",
        )
