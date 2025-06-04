from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from datetime import timedelta
import logging

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, CONF_HOST, CONF_NAME
from .api import AxeOSAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "button"]  # falls du Button behalten möchtest

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Wird aufgerufen, wenn ein Config Entry angelegt oder geladen wird."""
    host = entry.data[CONF_HOST]
    name = entry.data.get(CONF_NAME, host)

    # Gemeinsame aiohttp-Session von HA nutzen
    session = async_get_clientsession(hass)
    api = AxeOSAPI(session, host)

    async def async_update_data():
        """Fetch nur die System-Info vom Miner."""
        system_info = await api.get_system_info()
        if system_info is None:
            raise UpdateFailed(f"Kann System Info von {host} nicht abrufen")
        return system_info  # kein Swarm mehr

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{host}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    # Erstes Update, um Connectivity zu prüfen
    try:
        await coordinator.async_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Erst-Update fehlgeschlagen: {err}") from err

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady(f"Erst-Update nicht erfolgreich: {host}")

    # Speichere den Coordinator und API-Client in hass.data für Plattformen
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
        "host": host,
        "name": name,
    }

    # Gerät in Device Registry eintragen
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, host)},
        name=name,
        manufacturer="BitAxe",
        model=coordinator.data.get("boardVersion", "BitAxe Miner"),
        sw_version=coordinator.data.get("version", ""),
    )

    # Plattformen laden (nur Sensor + Button, falls gewünscht)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Wird aufgerufen, wenn der Config Entry entfernt wird."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
