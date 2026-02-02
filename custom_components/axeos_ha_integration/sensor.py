# ┌─────────────────────────────── Teil 1/2 ───────────────────────────────┐
"""Sensor platform for AxeOS-HA-Integration: only system info fields."""

from __future__ import annotations
import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# SENSOR_TYPES: Mapping of relevant fields from /api/system/info to Home Assistant
# key: internal identifier (unique_id suffix)
# value: Tuple (name suffix, unit, data_path, device_class, state_class, entity_category)
# data_path: key in coordinator.data (e.g. "power", "voltage", "hashRate", etc.)
# -------------------------------------------------------------------------
SENSOR_TYPES: dict[str, tuple[str, str | None, list[str], SensorDeviceClass | None, SensorStateClass | None, EntityCategory | None]] = {
    "power": ("Power Consumption", "W", ["power"], SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None),
    "voltage": ("Voltage", "mV", ["voltage"], SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, None),
    "current": ("Current", "mA", ["current"], SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, None),
    "temp": ("Chip Temperature", "°C", ["temp"], SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None),
    "vrTemp": ("VR Temperature", "°C", ["vrTemp"], SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None),
    "maxPower": ("Max Power", "W", ["maxPower"], SensorDeviceClass.POWER, None, EntityCategory.CONFIG),
    "minPower": ("Min Power", "W", ["minPower"], SensorDeviceClass.POWER, None, EntityCategory.CONFIG),
    "maxVoltage": ("Max Voltage", "V", ["maxVoltage"], SensorDeviceClass.VOLTAGE, None, EntityCategory.CONFIG),
    "minVoltage": ("Min Voltage", "V", ["minVoltage"], SensorDeviceClass.VOLTAGE, None, EntityCategory.CONFIG),
    "nominalVoltage": ("Nominal Voltage", "V", ["nominalVoltage"], SensorDeviceClass.VOLTAGE, None, EntityCategory.CONFIG),
    "hashRate": ("Current Hashrate", "H/s", ["hashRate"], None, SensorStateClass.MEASUREMENT, None),
    "hashRate_1m": ("Hashrate (1 minute)", "H/s", ["hashRate_1m"], None, SensorStateClass.MEASUREMENT, None),
    "hashRate_10m": ("Hashrate (10 minutes)", "H/s", ["hashRate_10m"], None, SensorStateClass.MEASUREMENT, None),
    "hashRate_1h": ("Hashrate (1 hour)", "H/s", ["hashRate_1h"], None, SensorStateClass.MEASUREMENT, None),
    "hashRate_1d": ("Hashrate (1 day)", "H/s", ["hashRate_1d"], None, SensorStateClass.MEASUREMENT, None),
    "expectedHashrate": ("Expected Hashrate", "H/s", ["expectedHashrate"], None, None, EntityCategory.DIAGNOSTIC),
    "bestDiff": ("Best Difficulty", None, ["bestDiff"], None, None, EntityCategory.DIAGNOSTIC),
    "bestSessionDiff": ("Best Session Difficulty", None, ["bestSessionDiff"], None, None, EntityCategory.DIAGNOSTIC),
    "poolDifficulty": ("Pool Difficulty", None, ["poolDifficulty"], None, None, EntityCategory.DIAGNOSTIC),
    "stratumDifficulty": ("Stratum Difficulty", None, ["stratumDifficulty"], None, None, EntityCategory.DIAGNOSTIC),
    "coreVoltage": ("Core Voltage Target", "mV", ["coreVoltage"], SensorDeviceClass.VOLTAGE, None, EntityCategory.CONFIG),
    "defaultCoreVoltage": ("Default Core Voltage", "mV", ["defaultCoreVoltage"], SensorDeviceClass.VOLTAGE, None, EntityCategory.CONFIG),
    "coreVoltageActual": ("Core Voltage Actual", "mV", ["coreVoltageActual", "coreVoltageActualMV"], SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, None),
    "frequency": ("Frequency", "MHz", ["frequency"], SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT, None),
    "ip": ("IP Address", None, ["ip", "hostip"], None, None, EntityCategory.DIAGNOSTIC),
    "ssid": ("WiFi SSID", None, ["ssid"], None, None, EntityCategory.DIAGNOSTIC),
    "macAddr": ("MAC Address", None, ["macAddr"], None, None, EntityCategory.DIAGNOSTIC),
    "hostname": ("Hostname", None, ["hostname"], None, None, EntityCategory.DIAGNOSTIC),
    "wifiStatus": ("WiFi Status", None, ["wifiStatus"], None, None, EntityCategory.DIAGNOSTIC),
    "wifiRSSI": ("WiFi Signal Strength", "dBm", ["wifiRSSI"], SensorDeviceClass.SIGNAL_STRENGTH, SensorStateClass.MEASUREMENT, EntityCategory.DIAGNOSTIC),
    "sharesAccepted": ("Accepted Shares", None, ["sharesAccepted"], None, SensorStateClass.TOTAL_INCREASING, None),
    "sharesRejected": ("Rejected Shares", None, ["sharesRejected"], None, SensorStateClass.TOTAL_INCREASING, None),
    "uptimeSeconds": ("Uptime", "s", ["uptimeSeconds"], SensorDeviceClass.DURATION, SensorStateClass.TOTAL_INCREASING, EntityCategory.DIAGNOSTIC),
    "freeHeap": ("Free Heap Memory", "bytes", ["freeHeap"], SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, EntityCategory.DIAGNOSTIC),
    "smallCoreCount": ("Total Core Count", None, ["smallCoreCount"], None, None, EntityCategory.DIAGNOSTIC),
    "asicCount": ("ASIC Count", None, ["asicCount"], None, None, EntityCategory.DIAGNOSTIC),
    "ASICModel": ("ASIC Model", None, ["ASICModel"], None, None, EntityCategory.DIAGNOSTIC),
    "stratumURL": ("Stratum URL", None, ["stratumURL"], None, None, EntityCategory.CONFIG),
    "stratumPort": ("Stratum Port", None, ["stratumPort"], None, None, EntityCategory.CONFIG),
    "stratumUser": ("Stratum User", None, ["stratumUser"], None, None, EntityCategory.CONFIG),
    "fallbackStratumURL": ("Fallback Stratum URL", None, ["fallbackStratumURL"], None, None, EntityCategory.CONFIG),
    "fallbackStratumPort": ("Fallback Stratum Port", None, ["fallbackStratumPort"], None, None, EntityCategory.CONFIG),
    "fallbackStratumUser": ("Fallback Stratum User", None, ["fallbackStratumUser"], None, None, EntityCategory.CONFIG),
    "fallbackStratumSuggestedDifficulty": ("Fallback Stratum Difficulty", None, ["fallbackStratumSuggestedDifficulty"], None, None, EntityCategory.CONFIG),
    "fallbackStratumExtranonceSubscribe": ("Fallback Stratum Extranonce Subscribe", None, ["fallbackStratumExtranonceSubscribe"], None, None, EntityCategory.CONFIG),
    "responseTime": ("API Response Time", "ms", ["responseTime"], SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT, EntityCategory.DIAGNOSTIC),
    "version": ("Firmware Version", None, ["version"], None, None, EntityCategory.DIAGNOSTIC),
    "axeOSVersion": ("AxeOS Version", None, ["axeOSVersion"], None, None, EntityCategory.DIAGNOSTIC),
    "idfVersion": ("IDF Version", None, ["idfVersion"], None, None, EntityCategory.DIAGNOSTIC),
    "boardVersion": ("Board Version", None, ["boardVersion", "deviceModel"], None, None, EntityCategory.DIAGNOSTIC),
    "fanspeed": ("Fan Speed (%)", "%", ["fanspeed"], None, SensorStateClass.MEASUREMENT, None),
    "manualFanSpeed": ("Manual Fan Speed", "%", ["manualFanSpeed"], None, SensorStateClass.MEASUREMENT, EntityCategory.CONFIG),
    "fanrpm": ("Fan RPM", "RPM", ["fanrpm"], None, SensorStateClass.MEASUREMENT, None),
    "temptarget": ("Temperature Target", "°C", ["temptarget", "pidTargetTemp"], SensorDeviceClass.TEMPERATURE, None, EntityCategory.CONFIG),
    "overheat_temp": ("Overheat Temperature", "°C", ["overheat_temp"], SensorDeviceClass.TEMPERATURE, None, EntityCategory.CONFIG),
    "statsFrequency": ("Stats Frequency", "s", ["statsFrequency"], SensorDeviceClass.DURATION, None, EntityCategory.CONFIG),
    "sharesRejectedReasons": ("Rejected Shares Reasons", None, ["sharesRejectedReasons"], None, None, EntityCategory.DIAGNOSTIC),
    # NerdAxe specific sensors
    "duplicateHWNonces": ("Duplicate HW Nonces", None, ["duplicateHWNonces"], None, SensorStateClass.TOTAL_INCREASING, EntityCategory.DIAGNOSTIC),
    "foundBlocks": ("Found Blocks (Session)", None, ["foundBlocks"], None, SensorStateClass.TOTAL_INCREASING, None),
    "totalFoundBlocks": ("Total Found Blocks", None, ["totalFoundBlocks"], None, SensorStateClass.TOTAL_INCREASING, None),
    "defaultFrequency": ("Default Frequency", "MHz", ["defaultFrequency"], SensorDeviceClass.FREQUENCY, None, EntityCategory.CONFIG),
    "vrFrequency": ("VR Frequency", "Hz", ["vrFrequency"], SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT, EntityCategory.DIAGNOSTIC),
    "defaultVrFrequency": ("Default VR Frequency", "Hz", ["defaultVrFrequency"], SensorDeviceClass.FREQUENCY, None, EntityCategory.CONFIG),
    "jobInterval": ("Job Interval", "ms", ["jobInterval"], SensorDeviceClass.DURATION, None, EntityCategory.CONFIG),
    "lastResetReason": ("Last Reset Reason", None, ["lastResetReason"], None, None, EntityCategory.DIAGNOSTIC),
    "runningPartition": ("Running Partition", None, ["runningPartition"], None, None, EntityCategory.DIAGNOSTIC),
    "defaultTheme": ("Default Theme", None, ["defaultTheme"], None, None, EntityCategory.CONFIG),
    "freeHeapInt": ("Free Heap (Internal)", "bytes", ["freeHeapInt"], SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, EntityCategory.DIAGNOSTIC),
    # PID Controller values
    "pidP": ("PID P Value", None, ["pidP"], None, None, EntityCategory.CONFIG),
    "pidI": ("PID I Value", None, ["pidI"], None, None, EntityCategory.CONFIG),
    "pidD": ("PID D Value", None, ["pidD"], None, None, EntityCategory.CONFIG),
    # Stratum pool details (nested in stratum object for NerdAxe)
    "stratum_poolMode": ("Pool Mode", None, ["stratum", "poolMode"], None, None, EntityCategory.DIAGNOSTIC),
    "stratum_activePoolMode": ("Active Pool Mode", None, ["stratum", "activePoolMode"], None, None, EntityCategory.DIAGNOSTIC),
    "stratum_poolBalance": ("Pool Balance", None, ["stratum", "poolBalance"], None, SensorStateClass.MEASUREMENT, EntityCategory.DIAGNOSTIC),
    "stratum_totalBestDiff": ("Stratum Total Best Difficulty", None, ["stratum", "totalBestDiff"], None, SensorStateClass.TOTAL_INCREASING, EntityCategory.DIAGNOSTIC),
    "stratum_poolDifficulty": ("Stratum Pool Difficulty", None, ["stratum", "poolDifficulty"], None, None, EntityCategory.DIAGNOSTIC),
}

def get_value(data: dict, keys: list[str]) -> any:
    """Get value from data dict, supporting nested keys.
    
    keys can be either:
    - Single strings like ["power", "voltage"] - tries each key
    - Nested path like ["stratum", "poolMode"] - follows the path in order
    """
    if not keys:
        return None
    
    # Check if this is a nested path (multi-element list where first element is a dict in data)
    if len(keys) > 1 and keys[0] in data and isinstance(data[keys[0]], dict):
        current = data
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        return current
    
    # Otherwise, try each key as an alternative
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
    for key, (suffix, unit, path, device_class, state_class, entity_category) in SENSOR_TYPES.items():
        # Skip temperature sensors if option is enabled
        if hide_temp_sensors and key in ["temp", "vrTemp", "temptarget"]:
            continue
            
        name = suffix
        unique_id = f"{host_id}_{key}"
        entities.append(
            AxeOSHASensor(
                coordinator, entry.entry_id, name, unique_id, unit, path, key,
                device_class, state_class, entity_category
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
        sensor_key: str = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        entity_category: EntityCategory | None = None,
    ) -> None:
        super().__init__(coordinator)
        self.entry_id = entry_id
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_entity_category = entity_category
        self.data_keys = data_keys
        self.sensor_key = sensor_key or (unique_id.split("_")[-1] if "_" in unique_id else unique_id)
        self._state = None
        
        # Set suggested display precision for specific sensors
        if sensor_key in ["hashRate", "expectedHashrate"]:
            self._attr_suggested_display_precision = 0
        elif sensor_key in ["power", "voltage", "current", "coreVoltageActual"]:
            self._attr_suggested_display_precision = 2
        elif sensor_key in ["temp", "vrTemp", "temptarget"]:
            self._attr_suggested_display_precision = 1
        elif sensor_key == "frequency":
            self._attr_suggested_display_precision = 0

    @property
    def native_value(self):
        return self._state
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self._state is not None

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
            "ip": "mdi:ip-network",
            "ssid": "mdi:wifi",
            "macAddr": "mdi:network",
            "hostname": "mdi:network",
        }
        key = self._attr_unique_id.split("_")[-1]
        return icons.get(key, "mdi:chip")

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
            "manufacturer": "BitAxe",
            "model": self.coordinator.data.get("boardVersion", "BitAxe Miner"),
            "sw_version": self.coordinator.data.get("version", ""),
        }
