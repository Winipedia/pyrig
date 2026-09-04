"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig_overrides.rig.tools.pyrigger import Pyrigger as OverridePyrigger
from pytest_mock import MockerFixture

from pyrig.rig.cli.commands.make.subclass import choose_subclass, make_subclass
from pyrig.rig.tools.pyrigger import Pyrigger


def test_make_subclass(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test function."""
    project_dir = tmp_path / "my-project"
    project_dir.mkdir()

    with chdir(project_dir):
        choose_subclass_mock = mocker.patch(
            choose_subclass.__module__ + "." + choose_subclass.__name__,
            return_value=OverridePyrigger,
        )

        make_subclass(None)

        choose_subclass_mock.assert_called_once()

        path = Path("src/my_project/rig/tools/pyrigger.py")

        assert path.exists()
        content = path.read_text()
        assert "class Pyrigger(BasePyrigger):" in content
        assert (
            "from pyrig_overrides.rig.tools.pyrigger import Pyrigger as BasePyrigger"
            in content
        )
        assert content.endswith("\n")
        assert (
            '"""\n\nfrom pyrig_overrides.rig.tools.pyrigger import Pyrigger as BasePyrigger'  # noqa: E501
            in content
        )
        assert "Pyrigger as BasePyrigger\n\n\nclass Pyrigger(BasePyrigger):" in content


def test_make_subclass_with_reference(
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    """Test function."""
    project_dir = tmp_path / "my-project"
    project_dir.mkdir()

    with chdir(project_dir):
        choose_subclass_mock = mocker.patch(
            choose_subclass.__module__ + "." + choose_subclass.__name__,
        )

        reference = (Pyrigger.__module__, Pyrigger.__name__)

        make_subclass(reference)

        choose_subclass_mock.assert_not_called()

        path = Path("src/my_project/rig/tools/pyrigger.py")

        assert path.exists()
        content = path.read_text()
        assert "class Pyrigger(BasePyrigger):" in content
        assert (
            "from pyrig.rig.tools.pyrigger import Pyrigger as BasePyrigger" in content
        )


def test_choose_subclass(mocker: MockerFixture) -> None:
    """Test function."""
    fuzzy_mock = mocker.patch("InquirerPy.inquirer.fuzzy")
    fuzzy_mock.return_value.execute.return_value = "module.ClassName"

    result = choose_subclass()
    assert result == "module.ClassName"
    fuzzy_mock.assert_called_once()
