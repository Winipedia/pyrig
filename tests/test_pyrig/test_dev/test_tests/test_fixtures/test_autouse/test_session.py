"""module for the following module path (maybe truncated).

tests.test_pyrig.test_testing.test_tests.test_base.test_scopes.test_session
"""

from pyrig.dev.tests.utils.decorators import skip_fixture_test


@skip_fixture_test
def test_assert_root_is_correct() -> None:
    """Test func for assert_config_files_are_correct."""
    raise NotImplementedError


@skip_fixture_test
def test_assert_no_namespace_packages() -> None:
    """Test func for assert_no_namespace_packages."""
    raise NotImplementedError


@skip_fixture_test
def test_assert_all_src_code_in_one_package() -> None:
    """Test func for assert_all_src_code_in_one_package."""
    raise NotImplementedError


@skip_fixture_test
def test_assert_src_package_correctly_named() -> None:
    """Test func for assert_src_package_correctly_named."""
    raise NotImplementedError


@skip_fixture_test
def test_assert_all_modules_tested() -> None:
    """Test func for assert_all_modules_tested."""
    raise NotImplementedError


@skip_fixture_test
def test_assert_no_unit_test_package_usage() -> None:
    """Test func for assert_no_unit_test_package_usage."""
    raise NotImplementedError


@skip_fixture_test
def test_assert_dependencies_are_up_to_date() -> None:
    """Test function."""
    raise NotImplementedError


@skip_fixture_test
def test_assert_pre_commit_is_installed() -> None:
    """Test function."""
    raise NotImplementedError


@skip_fixture_test
def test_assert_src_runs_without_dev_deps() -> None:
    """Test function."""
    raise NotImplementedError


@skip_fixture_test
def test_assert_src_does_not_use_dev() -> None:
    """Test function."""
    raise NotImplementedError


@skip_fixture_test
def test_assert_no_unstaged_changes() -> None:
    """Test function."""
    raise NotImplementedError
