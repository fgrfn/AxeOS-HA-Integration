"""Button-Platform für AxeOS Miner (Neustart)."""

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
    """Registriere die Restart-Button-Entity für jeden Miner."""
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    miner_name = hass.data[DOMAIN][entry.entry_id]["name"]
    host = hass.data[DOMAIN][entry.entry_id]["host"]

    async_add_entities(
        [AxeOSRestartButton(miner_name, host, api)],
        update_before_add=False,
    )

class AxeOSRestartButton(ButtonEntity):
    """Button, um den AxeOS Miner neuzustarten."""

    def __init__(self, miner_name: str, host: str, api: AxeOSAPI) -> None:
        """Initialisiere den Restart-Button."""
        self.miner_name = miner_name
        self.host = host
        self.api = api
        self._attr_name = f"{miner_name} Neustart"
        self._attr_icon = "mdi:restart"
        self._attr_unique_id = f"{host}_restart_button"

    async def async_press(self) -> None:
        """Wird aufgerufen, wenn der Button gedrückt wird."""
        _LOGGER.debug("Neustart für BitAxe %s (%s) angefordert", self.miner_name, self.host)
        success = await self.api.restart_system()
        if success:
            _LOGGER.info("Neustart erfolgreich gesendet an %s", self.host)
        else:
            _LOGGER.error("Neustart fehlgeschlagen für %s", self.host)
