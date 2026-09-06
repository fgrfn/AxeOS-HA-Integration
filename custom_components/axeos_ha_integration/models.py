"""Runtime data models for the AxeOS integration."""

from dataclasses import dataclass
from typing import Any, TypeAlias

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import AxeOSAPI


@dataclass(slots=True)
class AxeOSRuntimeData:
    """Non-persistent data associated with an AxeOS config entry."""

    coordinator: DataUpdateCoordinator[dict[str, Any]]
    api: AxeOSAPI
    host: str
    name: str


AxeOSConfigEntry: TypeAlias = ConfigEntry[AxeOSRuntimeData]
