"""Services for AxeOS-HA-Integration."""

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import logging

from .const import DOMAIN
from .api import AxeOSAPI

_LOGGER = logging.getLogger(__name__)

SERVICE_RESTART = "restart_miner"
SERVICE_SET_FREQUENCY = "set_frequency"
SERVICE_SET_VOLTAGE = "set_voltage"

SERVICE_RESTART_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
})

SERVICE_SET_FREQUENCY_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required("frequency"): vol.All(vol.Coerce(int), vol.Range(min=200, max=600)),
})

SERVICE_SET_VOLTAGE_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required("voltage"): vol.All(vol.Coerce(int), vol.Range(min=1000, max=1400)),
})


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for AxeOS integration."""

    async def handle_restart(call: ServiceCall) -> None:
        """Handle the restart service call."""
        entity_id = call.data["entity_id"]
        
        # Find the correct entry_id from entity registry
        for entry_id, data in hass.data[DOMAIN].items():
            api: AxeOSAPI = data.get("api")
            if api:
                _LOGGER.info(f"Restarting miner via service call: {entity_id}")
                await api.restart_system()
                return
        
        _LOGGER.error(f"Could not find miner for entity {entity_id}")

    async def handle_set_frequency(call: ServiceCall) -> None:
        """Handle the set_frequency service call."""
        entity_id = call.data["entity_id"]
        frequency = call.data["frequency"]
        
        _LOGGER.info(f"Service set_frequency called for {entity_id} with frequency={frequency}")
        _LOGGER.warning("Set frequency API endpoint not yet implemented in AxeOS API wrapper")
        # TODO: Implement when API supports PATCH /api/system
        # await api.set_frequency(frequency)

    async def handle_set_voltage(call: ServiceCall) -> None:
        """Handle the set_voltage service call."""
        entity_id = call.data["entity_id"]
        voltage = call.data["voltage"]
        
        _LOGGER.info(f"Service set_voltage called for {entity_id} with voltage={voltage}")
        _LOGGER.warning("Set voltage API endpoint not yet implemented in AxeOS API wrapper")
        # TODO: Implement when API supports PATCH /api/system
        # await api.set_voltage(voltage)

    hass.services.async_register(
        DOMAIN, SERVICE_RESTART, handle_restart, schema=SERVICE_RESTART_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_SET_FREQUENCY, handle_set_frequency, schema=SERVICE_SET_FREQUENCY_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_SET_VOLTAGE, handle_set_voltage, schema=SERVICE_SET_VOLTAGE_SCHEMA
    )

    _LOGGER.info("AxeOS services registered")


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services."""
    hass.services.async_remove(DOMAIN, SERVICE_RESTART)
    hass.services.async_remove(DOMAIN, SERVICE_SET_FREQUENCY)
    hass.services.async_remove(DOMAIN, SERVICE_SET_VOLTAGE)
    _LOGGER.info("AxeOS services unloaded")
