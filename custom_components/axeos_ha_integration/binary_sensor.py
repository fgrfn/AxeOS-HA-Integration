"""Binary Sensor platform for AxeOS-HA-Integration."""

from __future__ import annotations
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Binary sensor definitions
BINARY_SENSOR_TYPES: dict[str, tuple[str, list[str], BinarySensorDeviceClass | None, EntityCategory | None]] = {
    "overheat_mode": ("Overheat Mode", ["overheat_mode"], BinarySensorDeviceClass.PROBLEM, EntityCategory.DIAGNOSTIC),
    "isUsingFallbackStratum": ("Using Fallback Stratum", ["isUsingFallbackStratum", "stratum.usingFallback"], BinarySensorDeviceClass.CONNECTIVITY, EntityCategory.DIAGNOSTIC),
    "autofanspeed": ("Auto Fan Speed", ["autofanspeed"], None, None),
    "invertfanpolarity": ("Invert Fan Polarity", ["invertfanpolarity"], None, None),
    "flipscreen": ("Flip Screen", ["flipscreen"], None, None),
    "invertscreen": ("Invert Screen", ["invertscreen"], None, None),
    # NerdAxe specific binary sensors
    "shutdown": ("Shutdown", ["shutdown"], BinarySensorDeviceClass.PROBLEM, EntityCategory.DIAGNOSTIC),
    "autoscreenoff": ("Auto Screen Off", ["autoscreenoff"], None, None),
    "stratum_keep": ("Keep Stratum Connection", ["stratum_keep"], BinarySensorDeviceClass.CONNECTIVITY, EntityCategory.DIAGNOSTIC),
    "otp": ("One-Time Programming", ["otp"], None, EntityCategory.DIAGNOSTIC),
    "stratumEnonceSubscribe": ("Stratum Enonce Subscribe", ["stratumEnonceSubscribe"], None, EntityCategory.DIAGNOSTIC),
    "fallbackStratumEnonceSubscribe": ("Fallback Stratum Enonce Subscribe", ["fallbackStratumEnonceSubscribe"], None, EntityCategory.DIAGNOSTIC),
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
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    host = entry.data.get("host") or entry.entry_id
    host_id = str(host).replace(" ", "_").replace(".", "_").lower()

    entities: list[BinarySensorEntity] = []
    for key, (suffix, path, device_class, entity_category) in BINARY_SENSOR_TYPES.items():
        name = suffix
        unique_id = f"{host_id}_{key}"
        entities.append(
            AxeOSBinarySensor(
                coordinator, entry.entry_id, name, unique_id, path, key,
                device_class, entity_category
            )
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
        name: str,
        unique_id: str,
        data_keys: list[str],
        sensor_key: str,
        device_class: BinarySensorDeviceClass | None = None,
        entity_category: EntityCategory | None = None,
    ) -> None:
        super().__init__(coordinator)
        self.entry_id = entry_id
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_device_class = device_class
        self._attr_entity_category = entity_category
        self.data_keys = data_keys
        self.sensor_key = sensor_key

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
