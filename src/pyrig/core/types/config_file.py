"""Defines types related to configuration files."""

from typing import Any, TypeVar

type ConfigDict = dict[str, Any]
type ConfigList = list[Any]
type ConfigData = ConfigDict | ConfigList
ConfigT = TypeVar("ConfigT", bound=ConfigData)
