"""Button platform for AxeOS Miner (Restart)."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .api import AxeOSAPI

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Register the restart button entity for each miner."""
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    miner_name = hass.data[DOMAIN][entry.entry_id]["name"]
    host = hass.data[DOMAIN][entry.entry_id]["host"]

    async_add_entities(
        [AxeOSRestartButton(entry.entry_id, miner_name, host, api)],
        update_before_add=False,
    )

class AxeOSRestartButton(ButtonEntity):
    """Button to restart the AxeOS miner."""

    def __init__(self, entry_id: str, miner_name: str, host: str, api: AxeOSAPI) -> None:
        """Initialize the restart button."""
        self.entry_id = entry_id
        self.miner_name = miner_name
        self.host = host
        self.api = api
        self._attr_name = f"{miner_name} Restart"
        self._attr_icon = "mdi:restart"
        self._attr_unique_id = f"{host}_restart_button"

    async def async_press(self) -> None:
        """Called when the button is pressed."""
        _LOGGER.debug("Restart requested for BitAxe %s (%s)", self.miner_name, self.host)
        success = await self.api.restart_system()
        if success:
            _LOGGER.info("Restart successfully sent to %s", self.host)
        else:
            _LOGGER.error("Restart failed for %s", self.host)

    @property
    def device_info(self):
        # Falls du boardVersion und version im Setup hast, übergib sie als Parameter!
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
            "name": self.miner_name,
            "manufacturer": "BitAxe",
            "model": "BitAxe Miner",  # Fallback, falls keine Version verfügbar
            "sw_version": "",         # Fallback, falls keine Version verfügbar
        }

# Example for AxeOSAPI
import aiohttp

class AxeOSAPI:
    def __init__(self, host: str):
        self.host = host

    async def restart_system(self) -> bool:
        url = f"http://{self.host}/api/system/restart"
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as resp:
                return resp.status == 200
