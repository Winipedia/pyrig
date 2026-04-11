"""Defines types related to configuration files."""

from typing import Any

type ConfigDict = dict[str, Any]
type ConfigList = list[Any]
type ConfigData = ConfigDict | ConfigList
