"""Test module."""

from contextlib import chdir
from pathlib import Path

from pyrig.core.introspection.packages import (
    make_init_file,
    make_init_files,
    make_package_dir,
)


def test_make_init_file(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        path = Path.cwd() / "__init__.py"
        assert not path.exists()
        path, created = make_init_file(Path.cwd(), content="Hello")
        assert created
        assert path.exists()
        assert path.read_text() == "Hello"

        path, created = make_init_file(Path.cwd(), content="Hello")
        assert not created


def test_make_package_dir(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        path = Path() / "test" / "package" / "sub_package"
        make_package_dir(path, root=Path() / "test", content="")
        # `root` is the last directory processed and receives an __init__.py.
        assert (Path() / "test" / "__init__.py").exists()
        assert (Path() / "test" / "package" / "__init__.py").exists()
        assert (Path() / "test" / "package" / "sub_package" / "__init__.py").exists()
        assert not (Path() / "__init__.py").exists()


def test_make_init_files(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        assert not Path("__init__.py").exists()
        folder = Path("folder")
        folder2 = Path("folder2")
        folder_init = folder / "__init__.py"
        assert not folder_init.exists()
        folder.mkdir()
        folder2.mkdir()
        paths = make_init_files((Path(),), content="")
        assert len(paths) == 1
        assert Path("__init__.py").exists()
        paths = make_init_files((folder, folder2), content="")
        assert len(paths) == 2  # noqa: PLR2004
        assert folder_init.exists()
        assert (folder2 / "__init__.py").exists()

        paths = make_init_files((Path(), folder, folder2), content="")
        assert len(paths) == 0
