"""Tests module."""

from pathlib import Path

from pyrig.core.strings import (
    fstring_var_name,
    is_multiline,
    make_linked_badge_markdown,
    open_path_with_utf8,
    read_text_utf8,
    reformat_name,
    split_on_uppercase,
    write_text_utf8,
)
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger


def test_project_name_from_cwd() -> None:
    """Test function."""
    project_name = PackageManager.I.project_name()
    expected_project_name = Pyrigger.I.name()
    assert project_name == expected_project_name


def test_split_on_uppercase() -> None:
    """Test function."""
    # Test with simple string
    result = list(split_on_uppercase("HelloWorld"))
    assert result == ["Hello", "World"]

    # Test with multiple uppercase letters
    result = list(split_on_uppercase("SplitCamelCase"))
    assert result == ["Split", "Camel", "Case"], (
        f"Expected ['Split', 'Camel', 'Case'], got {result}"
    )

    # Test with all uppercase
    result = list(split_on_uppercase("ALLUPPERCASE"))
    assert result == list("ALLUPPERCASE"), (
        f"Expected {list('ALLUPPERCASE')}, got {result}"
    )

    # Test with all lowercase
    result = list(split_on_uppercase("alllowercase"))
    assert result == ["alllowercase"]

    # test with numbers
    result = list(split_on_uppercase("split1Camel2Case"))
    assert result == ["split1", "Camel2", "Case"], (
        f"Expected ['split1', 'Camel2', 'Case'], got {result}"
    )

    # entire sentence
    result = list(split_on_uppercase("Split some Camel Case"))
    expected = ["Split some ", "Camel ", "Case"]
    assert result == expected


def test_reformat_name() -> None:
    """Test function."""
    assert reformat_name("some_package", split_on="_", join_on="-") == "some-package"
    assert (
        reformat_name("some_package", split_on="_", join_on="-", capitalize=True)
        == "Some-Package"
    )
    assert (
        reformat_name("some_package", split_on="_", join_on="", capitalize=True)
        == "SomePackage"
    )
    assert reformat_name("__lead_trail__", split_on="_", join_on="-") == "lead-trail"


def test_make_linked_badge_markdown() -> None:
    """Test function."""
    result = make_linked_badge_markdown(
        image_url="https://example.com/badge.svg",
        link_url="https://example.com/",
        alt_text="Example Badge",
    )
    expected = "[![Example Badge](https://example.com/badge.svg)](https://example.com/)"
    assert result == expected


def test_read_text_utf8(tmp_path: Path) -> None:
    """Test function."""
    text = "Hello, world! 👋"
    file_path = tmp_path / "test.txt"
    file_path.write_text(text, encoding="utf-8")

    result = read_text_utf8(file_path)
    assert result == text

    # assert the function .read_text is not used in this project
    # to ensure consistent UTF-8 encoding handling
    source_path = PackageManager.I.source_root()
    for source_file in source_path.rglob("*.py"):
        content = source_file.read_text(encoding="utf-8")
        # skip the file if def read_text_utf8 is defined in it,
        # since it is the only one supposed to use .read_text internally
        if "def read_text_utf8(path: Path) -> str:" in content:
            continue
        assert ".read_text(" not in content, (
            f"Direct use of .read_text detected in {source_file}. "
            "Use read_text_utf8() instead for consistent UTF-8 handling."
        )


def test_write_text_utf8(tmp_path: Path) -> None:
    """Test function."""
    text = """Hello, world! 👋
This is a test file with multiple lines.
Another line here.
End of file.
"""
    file_path = tmp_path / "test_write.txt"
    write_text_utf8(file_path, text)

    result = file_path.read_text(encoding="utf-8")
    assert result == text

    # check all line ending are lf, not crlf, even on Windows
    content_bytes = file_path.read_bytes()
    assert b"\r\n" not in content_bytes

    # assert the function .write_text is not used in this project
    # to ensure consistent UTF-8 encoding handling
    source_path = PackageManager.I.source_root()
    for source_file in source_path.rglob("*.py"):
        content = source_file.read_text(encoding="utf-8")
        # skip the file if def write_text_utf8 is defined in it,
        # since it is the only one supposed to use .write_text internally
        if "def write_text_utf8(path: Path, content: str) -> int:" in content:
            continue
        assert ".write_text(" not in content, (
            f"Direct use of .write_text detected in {source_file}. "
            "Use write_text_utf8() instead for consistent UTF-8 handling."
        )


def test_open_path_with_utf8(tmp_path: Path) -> None:
    """Test function."""
    text = "Hello, world! 👋"
    file_path = tmp_path / "test_open.txt"
    file_path.write_text(text, encoding="utf-8")

    with open_path_with_utf8(file_path, mode="r") as f:
        result = f.read()
    assert result == text


def test_fstring_var_name() -> None:
    """Test function."""
    var = "value"
    assert fstring_var_name(f"{var=}") == "var"


def test_is_multiline() -> None:
    """Test function."""
    assert is_multiline("single line") is False
    assert is_multiline("first line\nsecond line") is True
    assert (
        is_multiline("""first line
second line""")
        is True
    )
    assert is_multiline("""One line only""") is False
