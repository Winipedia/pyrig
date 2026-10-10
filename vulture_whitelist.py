"""Explicit references for reviewed dead code false positives."""

from pyrig.rig.cli.make import inits, subcls
from pyrig.rig.cli.remove import pyc
from pyrig.rig.cli.subcommands import mk, rm, scratch
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.base.yaml import YAML_DUMP
from pyrig.rig.configs.community.code_of_conduct import CodeOfConductConfigFile
from pyrig.rig.configs.community.contributing import ContributingConfigFile
from pyrig.rig.configs.community.security import SecurityConfigFile
from pyrig.rig.configs.docs.builder import DocsBuilderConfigFile
from pyrig.rig.configs.docs.index import IndexConfigFile
from pyrig.rig.configs.py_typed import PyTypedConfigFile
from pyrig.rig.configs.python_version import PythonVersionConfigFile
from pyrig.rig.configs.version_control.attributes import (
    VersionControllerAttributesConfigFile,
)
from pyrig.rig.configs.version_control.ignore import VersionControllerIgnoreConfigFile
from pyrig.rig.configs.version_control.remote.codeowners import CodeownersConfigFile
from pyrig.rig.configs.version_control.remote.dependency_bot import (
    DependencyBotConfigFile,
)
from pyrig.rig.configs.version_control.remote.issue_templates.bug_report import (
    BugReportConfigFile,
)
from pyrig.rig.configs.version_control.remote.issue_templates.config import (
    ConfigConfigFile,
)
from pyrig.rig.configs.version_control.remote.issue_templates.feature_request import (
    FeatureRequestConfigFile,
)
from pyrig.rig.configs.version_control.remote.pull_request_template import (
    PullRequestTemplateConfigFile,
)
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.language.case_conflict import CaseConflictChecker
from pyrig.rig.tools.linting.ci_cd import CICDLinter
from pyrig.rig.tools.linting.json import JSONLinter
from pyrig.rig.tools.linting.xml import XMLLinter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.security.checker import SecurityChecker
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.large_files import LargeFileChecker
from pyrig.rig.tools.version_control.merge_conflict import MergeConflictChecker
from pyrig.rig.tools.version_control.remote.controller import RemoteVersionController

_COMMAND_GROUPS = (
    mk,
    rm,
)
_COMMANDS = (
    inits,
    pyc,
    scratch,
    subcls,
)
_CONFIG_FILES = (
    BugReportConfigFile,
    CodeOfConductConfigFile,
    CodeownersConfigFile,
    ConfigConfigFile,
    ContributingConfigFile,
    DependencyBotConfigFile,
    DocsBuilderConfigFile,
    FeatureRequestConfigFile,
    IndexConfigFile,
    PullRequestTemplateConfigFile,
    PythonVersionConfigFile,
    PyTypedConfigFile,
    SecurityConfigFile,
    VersionControllerAttributesConfigFile,
    VersionControllerIgnoreConfigFile,
    XMLLinter,
)
_DEPENDENCY_SUBCLASS_OVERRIDES = (
    ConfigFile.discovery_module,
    ConfigFile.merge_key,
    Tool.sort_key,
)
_LIBRARY_USAGES = (
    # https://github.com/Winipedia/pyrig-containers/blob/main/src/pyrig_containers/rig/configs/container_file.py
    PackageManager.install_dependencies_no_dev_args,
    # https://github.com/Winipedia/pyrig-fixtures/blob/main/src/pyrig_fixtures/rig/tests/fixtures/environment.py
    RemoteVersionController.running_in_ci,
    # https://github.com/Winipedia/pyrig-executables/blob/main/src/pyrig_executables/rig/configs/version_control/remote/workflows/release.py
    WorkflowConfigFile.strategy_matrix_os,
)
_TOOLS = (
    CaseConflictChecker,
    CICDLinter,
    JSONLinter,
    LargeFileChecker,
    MergeConflictChecker,
    SecurityChecker,
    TypeChecker,
)
_YAML_USAGES = (
    YAML_DUMP.compact_seq_map,
    YAML_DUMP.explicit_end,
    YAML_DUMP.explicit_start,
)
