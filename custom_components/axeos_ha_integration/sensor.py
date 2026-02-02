# ┌─────────────────────────────── Teil 1/2 ───────────────────────────────┐
"""Sensor platform for AxeOS-HA-Integration: only system info fields."""

from __future__ import annotations
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# SENSOR_TYPES: Mapping of relevant fields from /api/system/info to Home Assistant
# key: internal identifier (unique_id suffix)
# value: Tuple (name suffix, unit, data_path)
# data_path: key in coordinator.data (e.g. "power", "voltage", "hashRate", etc.)
# -------------------------------------------------------------------------
SENSOR_TYPES: dict[str, tuple[str, str | None, list[str]]] = {
    "power": ("Power Consumption", "W", ["power"]),
    "voltage": ("Voltage", "mV", ["voltage"]),
    "current": ("Current", "mA", ["current"]),
    "temp": ("Chip Temperature", "°C", ["temp"]),
    "vrTemp": ("VR Temperature", "°C", ["vrTemp"]),
    "maxPower": ("Max Power", "W", ["maxPower"]),
    "nominalVoltage": ("Nominal Voltage", "V", ["nominalVoltage"]),
    "hashRate": ("Current Hashrate", "H/s", ["hashRate"]),
    "expectedHashrate": ("Expected Hashrate", "H/s", ["expectedHashrate"]),
    "bestDiff": ("Best Difficulty", None, ["bestDiff"]),
    "bestSessionDiff": ("Best Session Difficulty", None, ["bestSessionDiff"]),
    "poolDifficulty": ("Pool Difficulty", None, ["poolDifficulty"]),
    "isUsingFallbackStratum": ("Fallback Stratum Active", None, ["isUsingFallbackStratum"]),
    "coreVoltage": ("Core Voltage Target", "mV", ["coreVoltage"]),
    "coreVoltageActual": ("Core Voltage Actual", "mV", ["coreVoltageActual"]),
    "frequency": ("Frequency", "MHz", ["frequency"]),
    "ssid": ("WiFi SSID", None, ["ssid"]),
    "macAddr": ("MAC Address", None, ["macAddr"]),
    "hostname": ("Hostname", None, ["hostname"]),
    "wifiStatus": ("WiFi Status", None, ["wifiStatus"]),
    "wifiRSSI": ("WiFi Signal Strength", "dBm", ["wifiRSSI"]),
    "sharesAccepted": ("Accepted Shares", None, ["sharesAccepted"]),
    "sharesRejected": ("Rejected Shares", None, ["sharesRejected"]),
    "uptimeSeconds": ("Uptime", "s", ["uptimeSeconds"]),
    "smallCoreCount": ("Total Core Count", None, ["smallCoreCount"]),
    "asicCount": ("ASIC Count", None, ["asicCount"]),
    "ASICModel": ("ASIC Model", None, ["ASICModel"]),
    "stratumURL": ("Stratum URL", None, ["stratumURL"]),
    "stratumPort": ("Stratum Port", None, ["stratumPort"]),
    "stratumUser": ("Stratum User", None, ["stratumUser"]),
    "fallbackStratumURL": ("Fallback Stratum URL", None, ["fallbackStratumURL"]),
    "fallbackStratumPort": ("Fallback Stratum Port", None, ["fallbackStratumPort"]),
    "fallbackStratumUser": ("Fallback Stratum User", None, ["fallbackStratumUser"]),
    "fallbackStratumSuggestedDifficulty": ("Fallback Stratum Difficulty", None, ["fallbackStratumSuggestedDifficulty"]),
    "fallbackStratumExtranonceSubscribe": ("Fallback Stratum Extranonce Subscribe", None, ["fallbackStratumExtranonceSubscribe"]),
    "responseTime": ("API Response Time", "ms", ["responseTime"]),
    "version": ("Firmware Version", None, ["version"]),
    "axeOSVersion": ("AxeOS Version", None, ["axeOSVersion"]),
    "idfVersion": ("IDF Version", None, ["idfVersion"]),
    "boardVersion": ("Board Version", None, ["boardVersion", "deviceModel"]),
    "overheat_mode": ("Overheat Mode", None, ["overheat_mode"]),
    "fanspeed": ("Fan Speed (%)", "%", ["fanspeed"]),
    "fanrpm": ("Fan RPM", "RPM", ["fanrpm"]),
    "temptarget": ("Temperature Target", "°C", ["temptarget"]),
    "statsFrequency": ("Stats Frequency", "s", ["statsFrequency"]),
    "sharesRejectedReasons": ("Rejected Shares Reasons", None, ["sharesRejectedReasons"]),
}

def get_value(data: dict, keys: list[str]) -> any:
    for key in keys:
        if key in data:
            return data[key]
    return None

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    # stabile host-id aus entry.data oder entry_id
    host = entry.data.get("host") or entry.entry_id
    host_id = str(host).replace(" ", "_").replace(".", "_").lower()
    
    # Get options
    hide_temp_sensors = entry.options.get("hide_temperature_sensors", False)

    entities: list[SensorEntity] = []
    miner_name = coordinator.data.get("hostname", "BitAxe")
    for key, (suffix, unit, path) in SENSOR_TYPES.items():
        # Skip temperature sensors if option is enabled
        if hide_temp_sensors and key in ["temp", "vrTemp", "temptarget"]:
            continue
            
        name = f"{miner_name} {suffix}"
        unique_id = f"{miner_name.lower()}_{key}"
        entities.append(
            AxeOSHASensor(
                coordinator, entry.entry_id, name, unique_id, unit, path, miner_name, key
            )
        )

    async_add_entities(entities)

class AxeOSHASensor(CoordinatorEntity, SensorEntity):
    """Generic sensor entity for an AxeOS-HA value."""

    _attr_has_entity_name = True
    entity_registry_enabled_default = True  # jetzt ab Werk aktiviert

    def __init__(
        self,
        coordinator,
        entry_id: str,
        name: str,
        unique_id: str,
        unit: str | None,
        data_keys: list[str],
        host_id: str,
        sensor_key: str = None,
    ) -> None:
        super().__init__(coordinator)
        self.entry_id = entry_id
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_native_unit_of_measurement = unit
        self.data_keys = data_keys
        self.host_id = host_id
        self.sensor_key = sensor_key or (unique_id.split("_")[-1] if "_" in unique_id else unique_id)
        self._state = None

    @property
    def native_value(self):
        return self._state

    def _get_value_from_data(self) -> any:
        return get_value(self.coordinator.data, self.data_keys)

    def _handle_coordinator_update(self) -> None:
        self._state = self._get_value_from_data()
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._handle_coordinator_update()

    @property
    def extra_state_attributes(self):
        attrs: dict[str, any] = {}
        if self.sensor_key == "sharesRejectedReasons":
            val = self.coordinator.data.get(self.data_keys[0])
            if isinstance(val, list):
                attrs["rejected_reasons"] = val
        if error := self.coordinator.data.get("last_error"):
            attrs["last_error"] = error
        if self.sensor_key == "hashRate" and (hist := self.coordinator.data.get("hashrate_history")):
            attrs.update({
                "hashrate_min": min(hist),
                "hashrate_max": max(hist),
                "hashrate_avg": sum(hist)/len(hist),
            })
        return attrs or None

    @property
    def icon(self):
        icons = {
            "power": "mdi:flash",
            "voltage": "mdi:flash-auto",
            "current": "mdi:current-ac",
            "temp": "mdi:thermometer",
            "vrTemp": "mdi:coolant-temperature",
            "hashRate": "mdi:chart-line",
            "expectedHashrate": "mdi:chart-bell-curve",
            "sharesAccepted": "mdi:check-circle-outline",
            "sharesRejected": "mdi:close-circle-outline",
            "uptimeSeconds": "mdi:clock-outline",
            "wifiRSSI": "mdi:wifi",
            "freeHeap": "mdi:memory",
            "fanspeed": "mdi:fan",
            "fanrpm": "mdi:fan-speed",
            "frequency": "mdi:speedometer",
            "coreVoltage": "mdi:power-plug",
            "coreVoltageActual": "mdi:power-plug-off",
        }
        key = self._attr_unique_id.split("_")[-1]
        return icons.get(key, "mdi:chip")

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
            "name": self.coordinator.data.get("hostname", self.host_id),
            "manufacturer": "BitAxe",
            "model": self.coordinator.data.get("boardVersion", "BitAxe Miner"),
            "sw_version": self.coordinator.data.get("version", ""),
        }


class AxeOSConnectionStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor to show if the miner is online."""

    _attr_has_entity_name = True
    entity_registry_enabled_default = True

    def __init__(self, coordinator, entry_id: str, host_id: str):
        super().__init__(coordinator)
        self.entry_id = entry_id
        self.host_id = host_id
        self._attr_name = f"{host_id} Connection Status"
        self._attr_unique_id = f"{host_id}_connection_status"
        self._attr_icon = "mdi:lan-connect"
        self._state = None

    @property
    def native_value(self):
        return "online" if not self.coordinator.data.get("last_error") else "offline"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._state = self.native_value
        self.async_write_ha_state()
