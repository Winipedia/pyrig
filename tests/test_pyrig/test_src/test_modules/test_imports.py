"""tests module."""

from contextlib import chdir
from pathlib import Path
from types import ModuleType

import pytest
from pytest_mock import MockFixture

from pyrig.src.modules.imports import (
    import_package_from_dir,
    import_package_with_dir_fallback,
    import_package_with_dir_fallback_with_default,
    iter_modules,
    module_is_package,
    walk_package,
)
from pyrig.src.modules.module import make_obj_importpath


def test_iter_modules(tmp_path: Path) -> None:
    """Test function."""
    # Create a temporary package with known content
    with chdir(tmp_path):
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        init_file = package_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        module_file = package_dir / "test_module.py"
        module_file.write_text('"""Test module."""\n')
        package = import_package_from_dir(package_dir)

        modules = iter_modules(package)
        modules_names = [m.__name__ for m, _ in modules]
        assert modules_names == [package.__name__ + ".test_module"], (
            f"Expected [package.test_module], got {modules}"
        )


def test_walk_package(mocker: MockFixture) -> None:
    """Test function."""
    # Create mock package hierarchy
    root_package = ModuleType("root")
    sub_package1 = ModuleType("root.sub1")
    sub_package2 = ModuleType("root.sub2")
    module1 = ModuleType("root.module1")
    module2 = ModuleType("root.sub1.module2")
    module3 = ModuleType("root.sub2.module3")

    # Mock iter_modules (walk_package calls iter_modules internally)
    mock_modules = mocker.patch(make_obj_importpath(iter_modules))

    # Define side effects for different packages
    # iter_modules now yields (module, is_package) tuples
    def side_effect(
        package: ModuleType,
    ) -> list[tuple[ModuleType, bool]]:
        if package == root_package:
            return [(sub_package1, True), (sub_package2, True), (module1, False)]
        if package == sub_package1:
            return [(module2, False)]
        if package == sub_package2:
            return [(module3, False)]
        return []

    mock_modules.side_effect = side_effect

    result = list(walk_package(root_package))
    # walk_package now yields (module, is_package) tuples
    expected = [
        (root_package, True),
        (sub_package1, True),
        (module2, False),
        (sub_package2, True),
        (module3, False),
        (module1, False),
    ]

    assert len(result) == len(expected), (
        f"Expected {len(expected)} results, got {len(result)}"
    )

    for i, (mod, is_pkg) in enumerate(result):
        expected_mod, expected_is_pkg = expected[i]
        assert mod == expected_mod, (
            f"Expected module {expected_mod}, got {mod} at index {i}"
        )
        assert is_pkg == expected_is_pkg, (
            f"Expected is_package={expected_is_pkg}, got {is_pkg} at index {i}"
        )


def test_module_is_package() -> None:
    """Test function."""
    # Create a mock module with __path__ attribute (package)
    mock_package = ModuleType("test_package")
    mock_package.__path__ = ["some/path"]

    # Create a mock module without __path__ attribute (regular module)
    mock_module = ModuleType("test_module")

    assert module_is_package(mock_package) is True, (
        "Expected module with __path__ to be identified as package"
    )

    assert module_is_package(mock_module) is False, (
        "Expected module without __path__ to not be identified as package"
    )


def test_import_package_with_dir_fallback(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        non_existing_dir = tmp_path / "non_existing"
        assert not non_existing_dir.exists()
        with pytest.raises(FileNotFoundError):
            import_package_with_dir_fallback(non_existing_dir)
        # import nonexisting againto ccheck if somehow cached in sy
        with pytest.raises(FileNotFoundError):
            import_package_with_dir_fallback(non_existing_dir)

        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        init_file = existing_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_package_with_dir_fallback(existing_dir)
        assert package.__name__ == "existing"


def test_import_package_from_dir(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        non_existing_dir = tmp_path / "non_existing"
        assert not non_existing_dir.exists()
        with pytest.raises(FileNotFoundError):
            import_package_from_dir(non_existing_dir)

        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        init_file = package_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_package_from_dir(package_dir)
        assert package.__name__ == "test_package"

        subdir = package_dir / "subdir"
        subdir.mkdir()
        init_file = subdir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_package_from_dir(subdir)
        assert package.__name__ == "test_package.subdir"


def test_import_package_with_dir_fallback_with_default() -> None:
    """Test function."""
    assert import_package_with_dir_fallback_with_default(Path("non_existing")) is None
    assert (
        import_package_with_dir_fallback_with_default(
            Path("non_existing"), default="default"
        )
        == "default"
    )
