"""Number platform for AxeOS HA Integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True)
class AxeOSNumberEntityDescription(NumberEntityDescription):
    """Describe an AxeOS number entity."""

    data_path: str


NUMBER_TYPES: tuple[AxeOSNumberEntityDescription, ...] = (
    AxeOSNumberEntityDescription(
        key="fanspeed", translation_key="fanspeed", native_unit_of_measurement="%",
        native_min_value=0, native_max_value=100, native_step=1,
        mode=NumberMode.SLIDER, icon="mdi:fan", data_path="fanspeed",
    ),
    AxeOSNumberEntityDescription(
        key="frequency", translation_key="frequency", native_unit_of_measurement="MHz",
        native_min_value=200, native_max_value=600, native_step=5,
        mode=NumberMode.BOX, icon="mdi:sine-wave", data_path="frequency",
    ),
    AxeOSNumberEntityDescription(
        key="coreVoltage", translation_key="corevoltage", native_unit_of_measurement="mV",
        native_min_value=1000, native_max_value=1400, native_step=10,
        mode=NumberMode.BOX, icon="mdi:lightning-bolt", data_path="coreVoltage",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AxeOS number entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    entities = []
    for description in NUMBER_TYPES:
        entities.append(
            AxeOSNumberEntity(
                coordinator,
                api,
                entry.entry_id,
                description,
            )
        )

    async_add_entities(entities)


class AxeOSNumberEntity(CoordinatorEntity, NumberEntity):
    """Representation of an AxeOS Number entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        api,
        entry_id: str,
        description: AxeOSNumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._api = api
        self._key = description.key
        self._data_path = description.data_path
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
        }

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._data_path)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        try:
            # Call the appropriate API method based on the key
            if self._key == "fanspeed":
                await self._api.set_fanspeed(int(value))
            elif self._key == "frequency":
                await self._api.set_frequency(int(value))
            elif self._key == "coreVoltage":
                await self._api.set_voltage(int(value))
            
            # Request coordinator update after setting value
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set %s to %s: %s", self._key, value, err)
