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

def get_logger(level):
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger

PLATFORMS = ["sensor", "button"]  # keep button if desired

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Called when a config entry is created or loaded."""
    logging_level = entry.options.get("logging_level", "info")
    _LOGGER = get_logger(logging_level)

    host = entry.data[CONF_HOST]
    name = entry.data.get(CONF_NAME, host)

    # Use shared aiohttp session from Home Assistant
    session = async_get_clientsession(hass)
    api = AxeOSAPI(session, host)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    async def async_update_data():
        # Now entry_data exists!
        system_info = await api.get_system_info()
        if system_info is None:
            raise UpdateFailed(f"Cannot fetch system info from {host}")

        hr = system_info.get("hashRate")
        if hr is not None:
            entry_data = hass.data[DOMAIN][entry.entry_id]
            history = entry_data.get("hashrate_history", [])
            history.append(hr)
            if len(history) > 100:
                history = history[-100:]
            entry_data["hashrate_history"] = history
            system_info["hashrate_history"] = history

        return system_info

    scan_interval = entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{host}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    # Initial update to check connectivity
    try:
        await coordinator.async_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Initial update failed: {err}") from err

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady(f"Initial update not successful: {host}")

    # Store coordinator and API client in hass.data for platforms
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
        "host": host,
        "name": name,
    }

    # Register device in device registry
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},  # <--- Fix hier!
        name=name,
        manufacturer="BitAxe",
        model=coordinator.data.get("boardVersion", "BitAxe Miner"),
        sw_version=coordinator.data.get("version", ""),
    )

    # Load platforms (sensor + button if desired)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Called when the config entry is removed."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def async_setup_options_flow(hass, entry):
    return AxeOSOptionsFlowHandler(entry)
