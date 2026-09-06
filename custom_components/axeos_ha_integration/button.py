"""Button platform for AxeOS Miner (Restart)."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import AxeOSAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Register the restart button entity for each miner."""
    api: AxeOSAPI = hass.data[DOMAIN][entry.entry_id]["api"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    miner_name: str = hass.data[DOMAIN][entry.entry_id]["name"]
    host: str = hass.data[DOMAIN][entry.entry_id]["host"]

    # stabile host_id aus entry.data oder entry_id
    host_id = str(host or entry.entry_id).replace(" ", "_").replace(".", "_").lower()

    async_add_entities(
        [AxeOSRestartButton(coordinator, entry.entry_id, miner_name, host_id, api)],
        update_before_add=False,
    )


class AxeOSRestartButton(CoordinatorEntity, ButtonEntity):
    """Button to restart the AxeOS miner."""

    _attr_has_entity_name = True
    entity_registry_enabled_default = True  # ab Werk aktiviert

    def __init__(
        self,
        coordinator,
        entry_id: str,
        miner_name: str,
        host_id: str,
        api: AxeOSAPI,
    ) -> None:
        """Initialize the restart button."""
        super().__init__(coordinator)
        self.entry_id = entry_id
        self.miner_name = miner_name
        self.host_id = host_id
        self.api = api

        self._attr_name = "Restart"
        self._attr_icon = "mdi:restart"
        self._attr_unique_id = f"{host_id}_restart_button"

    async def async_press(self) -> None:
        """Called when the button is pressed."""
        _LOGGER.debug(
            "Restart requested for BitAxe %s (%s)", self.miner_name, self.host_id
        )
        success = await self.api.restart_system()
        if not success:
            raise HomeAssistantError(f"Restart failed for {self.host_id}")
        _LOGGER.info("Restart successfully sent to %s", self.host_id)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        # Flexibles Mapping für Modell und Version
        info = self.coordinator.data or {}
        model = info.get("boardVersion") or info.get("deviceModel") or "BitAxe Miner"
        sw_version = info.get("version", "")
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
            "manufacturer": "BitAxe",
            "model": model,
            "sw_version": sw_version,
        }
