"""Binary Sensor platform for AxeOS-HA-Integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .models import AxeOSConfigEntry

_LOGGER = logging.getLogger(__name__)

# Binary sensor definitions
_BINARY_SENSOR_DEFINITIONS: dict[str, tuple[str, list[str], BinarySensorDeviceClass | None, EntityCategory | None]] = {
    "overheat_mode": ("Overheat Mode", ["overheat_mode"], BinarySensorDeviceClass.PROBLEM, EntityCategory.DIAGNOSTIC),
    "isUsingFallbackStratum": ("Using Fallback Stratum", ["isUsingFallbackStratum", "stratum.usingFallback"], BinarySensorDeviceClass.CONNECTIVITY, EntityCategory.DIAGNOSTIC),
    # NerdAxe specific binary sensors
    "shutdown": ("Shutdown", ["shutdown"], BinarySensorDeviceClass.PROBLEM, EntityCategory.DIAGNOSTIC),
    "stratum_keep": ("Keep Stratum Connection", ["stratum_keep"], BinarySensorDeviceClass.CONNECTIVITY, EntityCategory.DIAGNOSTIC),
    "otp": ("One-Time Programming", ["otp"], None, EntityCategory.DIAGNOSTIC),
    "stratumEnonceSubscribe": ("Stratum Enonce Subscribe", ["stratumEnonceSubscribe"], None, EntityCategory.DIAGNOSTIC),
    "fallbackStratumEnonceSubscribe": ("Fallback Stratum Enonce Subscribe", ["fallbackStratumEnonceSubscribe"], None, EntityCategory.DIAGNOSTIC),
}

@dataclass(frozen=True, kw_only=True)
class AxeOSBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe an AxeOS binary sensor."""

    data_keys: tuple[str, ...]


BINARY_SENSOR_TYPES: dict[str, AxeOSBinarySensorEntityDescription] = {
    key: AxeOSBinarySensorEntityDescription(
        key=key,
        translation_key=key.lower(),
        device_class=device_class,
        entity_category=entity_category,
        data_keys=tuple(path),
    )
    for key, (_name, path, device_class, entity_category) in _BINARY_SENSOR_DEFINITIONS.items()
}

def get_value(data: dict, keys: list[str]) -> bool | None:
    """Get value from data dict, trying multiple keys and supporting nested paths."""
    for key in keys:
        # Handle nested keys like "stratum.usingFallback"
        if "." in key:
            parts = key.split(".")
            current = data
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            if current is not None:
                val = current
            else:
                continue
        elif key in data:
            val = data[key]
        else:
            continue
        
        # Convert various representations to bool
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, str):
            return val.lower() in ['true', '1', 'on', 'yes']
    return None

async def async_setup_entry(
    hass: HomeAssistant,
    entry: AxeOSConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    coordinator = entry.runtime_data.coordinator
    host = entry.data.get("host") or entry.entry_id
    host_id = str(host).replace(" ", "_").replace(".", "_").lower()

    entities: list[BinarySensorEntity] = []
    for key, description in BINARY_SENSOR_TYPES.items():
        unique_id = f"{host_id}_{key}"
        entities.append(
            AxeOSBinarySensor(coordinator, entry.entry_id, unique_id, description)
        )

    async_add_entities(entities)


class AxeOSBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for AxeOS-HA boolean values."""

    _attr_has_entity_name = True
    entity_registry_enabled_default = True

    def __init__(
        self,
        coordinator,
        entry_id: str,
        unique_id: str,
        description: AxeOSBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self.entry_id = entry_id
        self._attr_unique_id = unique_id
        self.data_keys = list(description.data_keys)
        self.sensor_key = description.key

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return get_value(self.coordinator.data, self.data_keys)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.is_on is not None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
            "manufacturer": "BitAxe",
            "model": self.coordinator.data.get("boardVersion", "BitAxe Miner"),
            "sw_version": self.coordinator.data.get("version", ""),
        }
