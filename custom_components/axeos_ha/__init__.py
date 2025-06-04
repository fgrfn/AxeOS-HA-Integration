from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, CONF_HOST, CONF_NAME
from .api import AxeOSAPI

# …

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data[CONF_HOST]
    name = entry.data.get(CONF_NAME, host)

    session = async_get_clientsession(hass)
    api = AxeOSAPI(session, host)

    async def async_update_data():
        system_info = await api.get_system_info()
        if system_info is None:
            raise UpdateFailed(f"Kann System Info von {host} nicht abrufen")
        swarm_info = await api.get_swarm_info()
        return {
            "system": system_info,
            "swarm": swarm_info or {}
        }

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{host}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )
    # …
