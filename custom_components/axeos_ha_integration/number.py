"""Number platform for AxeOS HA Integration."""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Define number entities: (name, unit, data_path, min, max, step, mode, icon)
NUMBER_TYPES: dict[
    str, tuple[str, str | None, str, float, float, float, NumberMode, str]
] = {
    "fanspeed": (
        "Fan Speed",
        "%",
        "fanspeed",
        0,
        100,
        1,
        NumberMode.SLIDER,
        "mdi:fan",
    ),
    "frequency": (
        "Frequency",
        "MHz",
        "frequency",
        200,
        600,
        5,
        NumberMode.BOX,
        "mdi:sine-wave",
    ),
    "coreVoltage": (
        "Core Voltage",
        "mV",
        "coreVoltage",
        1000,
        1400,
        10,
        NumberMode.BOX,
        "mdi:lightning-bolt",
    ),
}


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
    for key, (
        name,
        unit,
        data_path,
        min_val,
        max_val,
        step,
        mode,
        icon,
    ) in NUMBER_TYPES.items():
        entities.append(
            AxeOSNumberEntity(
                coordinator,
                api,
                entry.entry_id,
                key,
                name,
                unit,
                data_path,
                min_val,
                max_val,
                step,
                mode,
                icon,
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
        key: str,
        name: str,
        unit: str | None,
        data_path: str,
        min_val: float,
        max_val: float,
        step: float,
        mode: NumberMode,
        icon: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._api = api
        self._key = key
        self._attr_name = name
        self._data_path = data_path
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = step
        self._attr_mode = mode
        self._attr_icon = icon
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
        return (
            self.coordinator.last_update_success and self.coordinator.data is not None
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        if self._key == "fanspeed":
            success = await self._api.set_fanspeed(int(value))
        elif self._key == "frequency":
            success = await self._api.set_frequency(int(value))
        elif self._key == "coreVoltage":
            success = await self._api.set_voltage(int(value))
        else:
            raise HomeAssistantError(f"Unsupported AxeOS setting: {self._key}")

        if not success:
            raise HomeAssistantError(f"Failed to set {self._key} to {value}")

        await self.coordinator.async_request_refresh()
