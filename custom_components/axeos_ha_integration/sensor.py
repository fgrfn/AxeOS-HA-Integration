"""Sensor-Platform für AxeOS-HA-Integration: nur System-Info-Felder."""

from __future__ import annotations
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# SENSOR_TYPES: Mapping der relevanten Felder aus /api/system/info auf Home Assistant
# key: interne Kennung (unique_id suffix)
# value: Tuple (Name-Suffix, Einheit, data_path)
# data_path: verschachtelter Pfad in coordinator.data (z.B. "power", "voltage", "hashRate" usw.)
# -------------------------------------------------------------------------
SENSOR_TYPES: dict[str, tuple[str, str | None, str]] = {
    "power":             ("Leistungsaufnahme", "W", "power"),
    "voltage":           ("Spannung", "mV", "voltage"),
    "current":           ("Strom", "mA", "current"),
    "temp":              ("Chip-Temperatur", "°C", "temp"),
    "vrTemp":            ("VR-Temperatur", "°C", "vrTemp"),
    "maxPower":          ("Maximale Leistung", "W", "maxPower"),
    "nominalVoltage":    ("Nominalspannung", "V", "nominalVoltage"),
    "hashRate":          ("Aktuelle Hashrate", "H/s", "hashRate"),
    "expectedHashrate":  ("Erwartete Hashrate", "H/s", "expectedHashrate"),
    "sharesAccepted":    ("Akzeptierte Shares", None, "sharesAccepted"),
    "sharesRejected":    ("Abgelehnte Shares", None, "sharesRejected"),
    "uptimeSeconds":     ("Betriebsdauer", "s", "uptimeSeconds"),
    "wifiRSSI":          ("WLAN-Signalstärke", "dBm", "wifiRSSI"),
    "freeHeap":          ("Freier Heap", "Bytes", "freeHeap"),
    "fanspeed":          ("Lüfterdrehzahl %-Anteil", "%", "fanspeed"),
    "fanrpm":            ("Lüfter-RPM", "RPM", "fanrpm"),
    "frequency":         ("Taktfrequenz", "MHz", "frequency"),
    "coreVoltage":       ("Kernspannung Soll", "mV", "coreVoltage"),
    "coreVoltageActual": ("Kernspannung Ist", "mV", "coreVoltageActual"),
    "asicCount":         ("Anzahl ASICs", None, "asicCount"),
    "smallCoreCount":    ("Anzahl Cores gesamt", None, "smallCoreCount"),
    "ASICModel":         ("ASIC-Modell", None, "ASICModel"),
    "version":           ("Firmware-Version", None, "version"),
    "ssid":              ("WLAN SSID", None, "ssid"),
    "macAddr":           ("MAC-Adresse", None, "macAddr"),
    "hostname":          ("Hostname", None, "hostname"),
    "wifiStatus":        ("WLAN-Status", None, "wifiStatus"),
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richte für jeden konfigurierten Miner die Sensor-Entities ein."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    miner_name = hass.data[DOMAIN][entry.entry_id]["name"]

    entities: list[SensorEntity] = []
    for key, (suffix, unit, data_path) in SENSOR_TYPES.items():
        entities.append(
            AxeOSHASensor(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                miner_name=miner_name,
                sensor_key=key,
                suffix=suffix,
                unit=unit,
                data_path=data_path,
            )
        )

    async_add_entities(entities, update_before_add=True)


class AxeOSHASensor(CoordinatorEntity, SensorEntity):
    """Allgemeine Sensor-Entity für einen AxeOS-HA-Wert (nur aus System-Info)."""

    def __init__(
        self,
        coordinator,
        entry_id: str,
        miner_name: str,
        sensor_key: str,
        suffix: str,
        unit: str | None,
        data_path: str,
    ) -> None:
        """Initialisiere den Sensor."""
        super().__init__(coordinator)
        self.entry_id = entry_id
        self.miner_name = miner_name
        self.sensor_key = sensor_key

        # Name: z.B. "BitAxe-Gamma Leistungsaufnahme"
        self._attr_name = f"{miner_name} {suffix}"
        self._attr_native_unit_of_measurement = unit
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

        # data_path ist jetzt ein einfacher Key (z.B. "power" oder "voltage")
        self.data_key = data_path

        # Unique ID: <host>_<sensor_key>, host kann aus coordinator.data["hostname"] kommen
        host = (coordinator.data.get("hostname") or entry_id).replace(" ", "_")
        self._attr_unique_id = f"{host}_{sensor_key}"

        self._state = None

    @property
    def native_value(self):
        """Gibt den aktuellen Wert zurück."""
        return self._state

    @property
    def device_class(self):
        """Setzt device_class, falls relevant."""
        if self.sensor_key in ("temp", "vrTemp"):
            return "temperature"
        if self.sensor_key == "uptimeSeconds":
            return "duration"
        if self.sensor_key == "wifiRSSI":
            return "signal_strength"
        return None

    @property
    def icon(self):
        """Icon pro Sensor-Typ."""
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
        """Liest den Wert aus coordinator.data anhand data_key aus."""
        data = self.coordinator.data
        return data.get(self.data_key)

    def _handle_coordinator_update(self) -> None:
        """Wird bei jedem Coordinator-Update ausgeführt."""
        self._state = self._get_value_from_data()
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Beim Einfügen der Entity: Setze ersten Wert."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
