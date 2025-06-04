"""BitAxe Integration für Home Assistant."""

import logging
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, CONF_HOST, CONF_NAME
from .api import AxeOSAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "button"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Wird aufgerufen, wenn ein Config Entry angelegt oder geladen wird."""
    host = entry.data[CONF_HOST]
    name = entry.data.get(CONF_NAME, host)

    # Gemeinsame aiohttp-Session von HA nutzen
    session = async_get_clientsession(hass)
    api = AxeOSAPI(session, host)

    # Update-Funktion, die System- und Swarm-Info abfragt
    async def async_update_data():
        """Fetch data from the BitAxe device."""
        system_info = await api.get_system_info()
        if system_info is None:
            raise UpdateFailed(f"Kann System Info von {host} nicht abrufen")
        swarm_info = await api.get_swarm_info()
        if swarm_info is None:
            raise UpdateFailed(f"Kann Swarm Info von {host} nicht abrufen")
        # Zusammenführen beider Ergebnisse in eine Struktur
        return {
            "system": system_info,
            "swarm": swarm_info
        }

    # Coordinator initialisieren (pollt alle X Sekunden)
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{host}",
        update_method=async_update_data,
        # Intervall aus const.py (in Sekunden)
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    # Erstes Update (um sicherzustellen, dass Gerät erreichbar ist)
    try:
        await coordinator.async_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Erst-Update fehlgeschlagen: {err}") from err

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady(f"Erst-Update nicht erfolgreich: {host}")

    # speichern in hass.data, damit Plattformen darauf zugreifen können
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
        "host": host,
        "name": name,
    }

    # Gerät im Device Registry eintragen, damit Entities gruppiert werden
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, host)},
        name=name,
        manufacturer="BitAxe",
        model=coordinator.data["system"].get("ASICModel", "AxeOS Miner"),
        sw_version=coordinator.data["system"].get("version", ""),
    )

    # Plattformen laden (sensor, button)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Wird aufgerufen, wenn der Config Entry entfernt wird."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
