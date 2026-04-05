"""Switch platform for AxeOS-HA-Integration: writable boolean settings."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Writable boolean settings: key -> (name, icon)
SWITCH_TYPES: dict[str, tuple[str, str]] = {
    "autofanspeed": ("Auto Fan Speed", "mdi:fan-auto"),
    "invertfanpolarity": ("Invert Fan Polarity", "mdi:fan-chevron-down"),
    "flipscreen": ("Flip Screen", "mdi:screen-rotation"),
    "invertscreen": ("Invert Screen", "mdi:invert-colors"),
    # NerdAxe specific
    "autoscreenoff": ("Auto Screen Off", "mdi:monitor-off"),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AxeOS switch entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    host = entry.data.get("host") or entry.entry_id
    host_id = str(host).replace(" ", "_").replace(".", "_").lower()

    entities = [
        AxeOSSwitchEntity(coordinator, api, entry.entry_id, host_id, key, name, icon)
        for key, (name, icon) in SWITCH_TYPES.items()
    ]
    async_add_entities(entities)


class AxeOSSwitchEntity(CoordinatorEntity, SwitchEntity):
    """Writable boolean setting for an AxeOS miner."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        api,
        entry_id: str,
        host_id: str,
        key: str,
        name: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator)
        self._api = api
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{host_id}_{key}"
        self._attr_icon = icon
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
        }

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        val = self.coordinator.data.get(self._key)
        if val is None:
            return None
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, str):
            return val.lower() in ("true", "1", "on", "yes")
        return None

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self._key in self.coordinator.data
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        ok = await self._api.set_setting(self._key, True)
        if not ok:
            _LOGGER.error("Failed to enable %s", self._key)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        ok = await self._api.set_setting(self._key, False)
        if not ok:
            _LOGGER.error("Failed to disable %s", self._key)
        await self.coordinator.async_request_refresh()
