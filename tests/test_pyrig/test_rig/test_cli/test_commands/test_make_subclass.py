"""module."""

from contextlib import chdir
from pathlib import Path

from pytest_mock import MockerFixture

from pyrig.rig.cli.commands.make_subclass import choose_subclass, make_subclass
from pyrig.rig.tools.pyrigger import Pyrigger


def test_make_subclass(tmp_path: Path) -> None:
    """Test function."""
    project_dir = tmp_path / "my-project"
    project_dir.mkdir()

    with chdir(project_dir):
        cls = Pyrigger

        import_path = f"{cls.__module__}.{cls.__name__}"

        make_subclass(import_path)

        path = Path("src/my_project/rig/tools/pyrigger.py")

        assert path.exists()
        content = path.read_text()
        assert "class Pyrigger(BasePyrigger):" in content
        assert (
            "from pyrig.rig.tools.pyrigger import Pyrigger as BasePyrigger" in content
        )
        assert content.endswith("\n")
        assert (
            '"""\n\nfrom pyrig.rig.tools.pyrigger import Pyrigger as BasePyrigger'
            in content
        )
        assert "Pyrigger as BasePyrigger\n\n\nclass Pyrigger(BasePyrigger):" in content


def test_choose_subclass(mocker: MockerFixture) -> None:
    """Test function."""
    fuzzy_mock = mocker.patch("InquirerPy.inquirer.fuzzy")
    fuzzy_mock.return_value.execute.return_value = "module.ClassName"

    result = choose_subclass()
    assert result == "module.ClassName"
    fuzzy_mock.assert_called_once()
