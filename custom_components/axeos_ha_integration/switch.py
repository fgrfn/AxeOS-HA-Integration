"""Switch platform for AxeOS-HA-Integration: writable boolean settings."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True)
class AxeOSSwitchEntityDescription(SwitchEntityDescription):
    """Describe an AxeOS switch."""


SWITCH_TYPES: tuple[AxeOSSwitchEntityDescription, ...] = (
    AxeOSSwitchEntityDescription(key="autofanspeed", translation_key="autofanspeed", icon="mdi:fan-auto"),
    AxeOSSwitchEntityDescription(key="invertfanpolarity", translation_key="invertfanpolarity", icon="mdi:fan-chevron-down"),
    AxeOSSwitchEntityDescription(key="flipscreen", translation_key="flipscreen", icon="mdi:screen-rotation"),
    AxeOSSwitchEntityDescription(key="invertscreen", translation_key="invertscreen", icon="mdi:invert-colors"),
    AxeOSSwitchEntityDescription(key="autoscreenoff", translation_key="autoscreenoff", icon="mdi:monitor-off"),
)


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
        AxeOSSwitchEntity(coordinator, api, entry.entry_id, host_id, description)
        for description in SWITCH_TYPES
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
        description: AxeOSSwitchEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._api = api
        self._key = description.key
        self._attr_unique_id = f"{host_id}_{description.key}"
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
