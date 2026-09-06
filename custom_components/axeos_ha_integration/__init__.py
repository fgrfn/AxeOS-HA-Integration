import logging
from datetime import timedelta

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AxeOSAPI
from .const import CONF_HOST, CONF_NAME, DEFAULT_SCAN_INTERVAL, DOMAIN
from .models import AxeOSConfigEntry, AxeOSRuntimeData
from .services import async_setup_services, async_unload_services


def get_logger(level):
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
]

async def async_setup_entry(hass: HomeAssistant, entry: AxeOSConfigEntry) -> bool:
    """Called when a config entry is created or loaded."""
    logging_level = entry.options.get("logging_level", "info")
    _LOGGER = get_logger(logging_level)

    host = entry.data[CONF_HOST]
    name = entry.data.get(CONF_NAME, host)

    # Use shared aiohttp session from Home Assistant
    session = async_get_clientsession(hass)
    api = AxeOSAPI(session, host)

    hashrate_history: list[float] = []

    async def async_update_data():
        system_info = await api.get_system_info()
        if system_info is None:
            raise UpdateFailed(f"Cannot fetch system info from {host}")

        hr = system_info.get("hashRate")
        if hr is not None:
            hashrate_history.append(hr)
            if len(hashrate_history) > 100:
                del hashrate_history[:-100]
            system_info["hashrate_history"] = hashrate_history.copy()

        return system_info

    scan_interval = entry.options.get("scan_interval", entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL))
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        config_entry=entry,
        name=f"{DOMAIN}_{host}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    # Initial update to check connectivity; raises ConfigEntryNotReady on failure
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = AxeOSRuntimeData(
        coordinator=coordinator,
        api=api,
        host=host,
        name=name,
    )

    # Register device in device registry
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name=name,
        manufacturer="BitAxe",
        model=coordinator.data.get("boardVersion", "BitAxe Miner"),
        sw_version=coordinator.data.get("version", ""),
    )

    # Load platforms (sensor + button if desired)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Setup services
    await async_setup_services(hass)

    # Reload entry when options change
    async def _async_update_listener(hass: HomeAssistant, entry: AxeOSConfigEntry) -> None:
        await hass.config_entries.async_reload(entry.entry_id)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: AxeOSConfigEntry) -> bool:
    """Called when the config entry is removed."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok and len(hass.config_entries.async_loaded_entries(DOMAIN)) <= 1:
        await async_unload_services(hass)
            
    return unload_ok
