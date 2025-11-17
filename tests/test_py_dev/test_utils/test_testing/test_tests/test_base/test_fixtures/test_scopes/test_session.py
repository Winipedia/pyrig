"""module for the following module path (maybe truncated).

tests.test_py_dev.test_testing.test_tests.test_base.test_scopes.test_session
"""

from py_dev.utils.testing.skip import skip_fixture_test


@skip_fixture_test
def test_assert_dev_dependencies_config_is_correct() -> None:
    """Test func for assert_dev_dependencies_config_is_correct."""
    raise NotImplementedError


@skip_fixture_test
def test_assert_config_files_are_correct() -> None:
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
def test_assert_no_dev_usage_in_non_dev_files() -> None:
    """Test func for assert_no_dev_usage_in_non_dev_files."""
    raise NotImplementedError
