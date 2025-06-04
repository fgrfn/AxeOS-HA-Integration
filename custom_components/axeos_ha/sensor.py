"""Sensor-Platform für AxeOS Miner (erweiterte Version mit allen system/info-Feldern)."""

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

# ---------------------------------------------------------------------------------------
#   SENSOR_TYPES: Mapping aller relevanten Felder aus /api/system/info auf Home Assistant
# ---------------------------------------------------------------------------------------
SENSOR_TYPES: dict[str, tuple[str, str | None, str]] = {
    "power":             ("Leistungsaufnahme", "W", "system.power"),
    "voltage":           ("Spannung", "mV", "system.voltage"),
    "current":           ("Strom", "mA", "system.current"),
    "temp":              ("Chip-Temperatur", "°C", "system.temp"),
    "vrTemp":            ("VR-Temperatur", "°C", "system.vrTemp"),
    "maxPower":          ("Maximale Leistung", "W", "system.maxPower"),
    "nominalVoltage":    ("Nominalspannung", "V", "system.nominalVoltage"),
    "hashRate":          ("Aktuelle Hashrate", "H/s", "system.hashRate"),
    "expectedHashrate":  ("Erwartete Hashrate", "H/s", "system.expectedHashrate"),
    "sharesAccepted":    ("Akzeptierte Shares", None, "system.sharesAccepted"),
    "sharesRejected":    ("Abgelehnte Shares", None, "system.sharesRejected"),
    "uptimeSeconds":     ("Betriebsdauer", "s", "system.uptimeSeconds"),
    "wifiRSSI":          ("WLAN-Signalstärke", "dBm", "system.wifiRSSI"),
    "freeHeap":          ("Freier Heap", "Bytes", "system.freeHeap"),
    "fanspeed":          ("Lüfterdrehzahl %-Anteil", "%", "system.fanspeed"),
    "fanrpm":            ("Lüfter-RPM", "RPM", "system.fanrpm"),
    "frequency":         ("Taktfrequenz", "MHz", "system.frequency"),
    "coreVoltage":       ("Kernspannung Soll", "mV", "system.coreVoltage"),
    "coreVoltageActual": ("Kernspannung Ist", "mV", "system.coreVoltageActual"),
    "asicCount":         ("Anzahl ASICs", None, "system.asicCount"),
    "smallCoreCount":    ("Anzahl Cores gesamt", None, "system.smallCoreCount"),
    "ASICModel":         ("ASIC-Modell", None, "system.ASICModel"),
    "version":           ("Firmware-Version", None, "system.version"),
    "ssid":              ("WLAN SSID", None, "system.ssid"),
    "macAddr":           ("MAC-Adresse", None, "system.macAddr"),
    "hostname":          ("Hostname", None, "system.hostname"),
    "wifiStatus":        ("WLAN-Status", None, "system.wifiStatus"),
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
            AxeOSSensor(
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


class AxeOSSensor(CoordinatorEntity, SensorEntity):
    """Allgemeine Sensor-Entity für einen BitAxe-Miner-Wert."""

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
        # z. B. "Miner1 Chip-Temperatur"
        self._attr_name = f"{miner_name} {suffix}"
        self._attr_native_unit_of_measurement = unit
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

        # data_path als Liste aufsplitten, z.B. "system.temp" → ["system","temp"]
        self.data_path = data_path.split(".")

        # Unique ID: <host>_<sensor_key>
        try:
            host = coordinator.data["system"].get("hostname", entry_id)
        except Exception:
            host = entry_id
        self._attr_unique_id = f"{host}_{sensor_key}"

        self._state = None

    @property
    def native_value(self):
        """Gibt den aktuellen wert zurück."""
        return self._state

    @property
    def device_class(self):
        """Setzt bei Temperatur- oder Dauer-Sensoren die device_class."""
        if self.sensor_key in ("temp", "vrTemp"):
            return "temperature"
        if self.sensor_key == "uptimeSeconds":
            return "duration"
        if self.sensor_key in ("wifiRSSI",):
            return "signal_strength"
        return None

    @property
    def icon(self):
        """Gibt ein passendes Icon zurück je nach Sensor-Typ."""
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
        """Liest den verschachtelten Wert aus coordinator.data anhand von data_path aus."""
        data = self.coordinator.data
        try:
            for key in self.data_path:
                if data is None:
                    return None
                data = data.get(key)
            return data
        except Exception:
            return None

    def _handle_coordinator_update(self) -> None:
        """Wird bei jedem Coordinator-Update ausgeführt."""
        raw = self._get_value_from_data()
        self._state = raw
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Beim Einfügen der Entity wird direkt ein erster Status-Wert gesetzt."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
