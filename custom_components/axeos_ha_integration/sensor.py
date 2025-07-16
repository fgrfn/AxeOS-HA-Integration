"""Sensor platform for AxeOS-HA-Integration: only system info fields."""

from __future__ import annotations
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import EntityCategory
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
    "isPSRAMAvailable": ("PSRAM Available", None, ["isPSRAMAvailable"]),
    "freeHeap": ("Free Heap", "Bytes", ["freeHeap"]),
    "coreVoltage": ("Core Voltage Target", "mV", ["coreVoltage"]),
    "coreVoltageActual": ("Core Voltage Actual", "mV", ["coreVoltageActual"]),
    "frequency": ("Frequency", "MHz", ["frequency"]),
    "ssid": ("WiFi SSID", None, ["ssid"]),
    "macAddr": ("MAC Address", None, ["macAddr"]),
    "hostname": ("Hostname", None, ["hostname"]),
    "wifiStatus": ("WiFi Status", None, ["wifiStatus"]),
    "wifiRSSI": ("WiFi Signal Strength", "dBm", ["wifiRSSI"]),
    "apEnabled": ("Access Point Enabled", None, ["apEnabled"]),
    "sharesAccepted": ("Accepted Shares", None, ["sharesAccepted"]),
    "sharesRejected": ("Rejected Shares", None, ["sharesRejected"]),
    "uptimeSeconds": ("Uptime", "s", ["uptimeSeconds"]),
    "smallCoreCount": ("Total Core Count", None, ["smallCoreCount"]),
    "asicCount": ("ASIC Count", None, ["asicCount"]),
    "ASICModel": ("ASIC Model", None, ["ASICModel"]),
    "stratumURL": ("Stratum URL", None, ["stratumURL"]),
    "stratumPort": ("Stratum Port", None, ["stratumPort"]),
    "stratumUser": ("Stratum User", None, ["stratumUser"]),
    "stratumSuggestedDifficulty": ("Stratum Difficulty", None, ["stratumSuggestedDifficulty"]),
    "stratumExtranonceSubscribe": ("Stratum Extranonce Subscribe", None, ["stratumExtranonceSubscribe"]),
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
    "runningPartition": ("Running Partition", None, ["runningPartition"]),
    "overheat_mode": ("Overheat Mode", None, ["overheat_mode"]),
    "overclockEnabled": ("Overclock Enabled", None, ["overclockEnabled"]),
    "display": ("Display", None, ["display"]),
    "rotation": ("Display Rotation", None, ["rotation", "flipscreen"]),
    "invertscreen": ("Invert Screen", None, ["invertscreen"]),
    "displayTimeout": ("Display Timeout", "s", ["displayTimeout", "autoscreenoff"]),
    "autofanspeed": ("Auto Fan Speed", None, ["autofanspeed"]),
    "fanspeed": ("Fan Speed (%)", "%", ["fanspeed"]),
    "fanrpm": ("Fan RPM", "RPM", ["fanrpm"]),
    "temptarget": ("Temperature Target", "°C", ["temptarget"]),
    "statsFrequency": ("Stats Frequency", "s", ["statsFrequency"]),
    # Complex fields like "sharesRejectedReasons" can be represented as JSON string:
    "sharesRejectedReasons": ("Rejected Shares Reasons", None, ["sharesRejectedReasons"]),
}

def get_value(data, keys):
    for key in keys:
        if key in data:
            return data[key]
    return None

def validate_sensor_types():
    """Validate the structure of SENSOR_TYPES dictionary."""
    for key, value in SENSOR_TYPES.items():
        if not isinstance(value, tuple) or len(value) != 3:
            _LOGGER.error("Invalid SENSOR_TYPES entry for %s: expected tuple of length 3, got %s", key, value)
            continue
        
        name_suffix, unit, data_path = value
        if not isinstance(name_suffix, str):
            _LOGGER.error("Invalid name_suffix for %s: expected str, got %s", key, type(name_suffix))
        if unit is not None and not isinstance(unit, str):
            _LOGGER.error("Invalid unit for %s: expected str or None, got %s", key, type(unit))
        if not isinstance(data_path, list) or not data_path:
            _LOGGER.error("Invalid data_path for %s: expected non-empty list, got %s", key, data_path)

# Validate sensor types at module load
validate_sensor_types()

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    miner_name = hass.data[DOMAIN][entry.entry_id]["name"]
    data = coordinator.data

    entities = []
    for key, (name_suffix, unit, data_path) in SENSOR_TYPES.items():
        # Validate SENSOR_TYPES entry structure
        if not isinstance(name_suffix, str) or not isinstance(data_path, list):
            _LOGGER.error("Invalid SENSOR_TYPES entry for %s: name_suffix=%s, data_path=%s", 
                         key, name_suffix, data_path)
            continue
            
        value = get_value(data, data_path)
        if value is not None:
            try:
                entities.append(AxeOSHASensor(coordinator, entry.entry_id, miner_name, key, name_suffix, unit, data_path))
                _LOGGER.debug("Created sensor entity for %s: %s", key, name_suffix)
            except Exception as err:
                _LOGGER.error("Failed to create sensor entity for %s: %s", key, err)
        else:
            _LOGGER.debug("Skipping sensor %s: no data available in coordinator.data", key)

    if not entities:
        _LOGGER.warning("No sensor entities were created. Check if coordinator data is available and valid.")
    else:
        _LOGGER.info("Created %d sensor entities", len(entities))

    async_add_entities(entities)


class AxeOSHASensor(CoordinatorEntity, SensorEntity):
    """Generic sensor entity for an AxeOS-HA value (from system info only)."""

    _attr_entity_registry_enabled_default = True

    def __init__(
        self,
        coordinator,
        entry_id: str,
        miner_name: str,
        sensor_key: str,
        suffix: str,
        unit: str | None,
        data_path: list[str],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry_id = entry_id
        self.miner_name = miner_name
        self.sensor_key = sensor_key

        # Name: e.g. "BitAxe-Gamma Power Consumption"
        self._attr_name = f"{miner_name} {suffix}"
        self._attr_native_unit_of_measurement = unit
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

        # data_path is now a simple key (e.g. "power" or "voltage")
        self.data_keys = data_path

        # Unique ID: <host>_<sensor_key>, host can be from coordinator.data["hostname"]
        host = (coordinator.data.get("hostname") or entry_id).replace(" ", "_")
        self._attr_unique_id = f"{host}_{sensor_key}"

        self._state = None

    @property
    def native_value(self):
        """Returns the current value."""
        return self._state

    @property
    def device_class(self):
        """Sets device_class if relevant."""
        if self.sensor_key in ("temp", "vrTemp"):
            return "temperature"
        if self.sensor_key == "uptimeSeconds":
            return "duration"
        if self.sensor_key == "wifiRSSI":
            return "signal_strength"
        return None

    @property
    def icon(self):
        """Icon per sensor type."""
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
            "asicCount": "mdi:chip-outline",
            "smallCoreCount": "mdi:chip",
            "ASICModel": "mdi:chip",
            "version": "mdi:chip",
            "ssid": "mdi:wifi",
            "macAddr": "mdi:ethernet",
            "hostname": "mdi:home",
            "wifiStatus": "mdi:access-point-network",
        }
        return icons.get(self.sensor_key)

    def _get_value_from_data(self) -> any:
        """Reads the value from coordinator.data using data_keys."""
        try:
            data = self.coordinator.data
            if not data:
                _LOGGER.debug("No coordinator data available for sensor %s", self.sensor_key)
                return None
            
            value = get_value(data, self.data_keys)
            if value is None:
                _LOGGER.debug("No value found for sensor %s with data_keys %s", self.sensor_key, self.data_keys)
            return value
        except Exception as err:
            _LOGGER.error("Error getting value for sensor %s: %s", self.sensor_key, err)
            return None

    def _handle_coordinator_update(self) -> None:
        """Executed on every coordinator update."""
        try:
            new_state = self._get_value_from_data()
            if new_state != self._state:
                _LOGGER.debug("State changed for sensor %s: %s -> %s", self.sensor_key, self._state, new_state)
            self._state = new_state
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Error updating sensor %s: %s", self.sensor_key, err)

    async def async_added_to_hass(self) -> None:
        """When the entity is added: set initial value."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()

    @property
    def extra_state_attributes(self):
        """Return additional attributes for the sensor."""
        attrs = {}

        # Show rejected reasons as attribute for the relevant sensor
        if self.sensor_key == "sharesRejectedReasons":
            value = get_value(self.coordinator.data, self.data_keys)
            if isinstance(value, list):
                attrs["rejected_reasons"] = value

        # Add last error status if available
        error = self.coordinator.data.get("last_error")
        if error:
            attrs["last_error"] = error

        # Example: Add historical min/max/avg hash rate
        if self.sensor_key == "hashRate":
            history = self.coordinator.data.get("hashrate_history", [])
            if history:
                attrs["hashrate_min"] = min(history)
                attrs["hashrate_max"] = max(history)
                attrs["hashrate_avg"] = sum(history) / len(history)

        return attrs if attrs else None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
            "name": self.miner_name,
            "manufacturer": "BitAxe",
            "model": self.coordinator.data.get("boardVersion", "BitAxe Miner"),
            "sw_version": self.coordinator.data.get("version", ""),
        }


class AxeOSConnectionStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor to show if the miner is online."""

    def __init__(self, coordinator, entry_id, miner_name):
        super().__init__(coordinator)
        self._attr_name = f"{miner_name} Connection Status"
        self._attr_unique_id = f"{entry_id}_connection_status"
        self._attr_icon = "mdi:lan-connect"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        # You can set this in your coordinator or API code
        return "online" if not self.coordinator.data.get("last_error") else "offline"
