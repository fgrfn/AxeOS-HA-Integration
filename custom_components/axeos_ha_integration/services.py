"""Services for AxeOS-HA-Integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

from .api import AxeOSAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_RESTART = "restart_miner"
SERVICE_SET_FREQUENCY = "set_frequency"
SERVICE_SET_VOLTAGE = "set_voltage"

SERVICE_RESTART_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
    }
)

SERVICE_SET_FREQUENCY_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("frequency"): vol.All(vol.Coerce(int), vol.Range(min=200, max=600)),
    }
)

SERVICE_SET_VOLTAGE_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("voltage"): vol.All(vol.Coerce(int), vol.Range(min=1000, max=1400)),
    }
)


def _resolve_api_for_entity(hass: HomeAssistant, entity_id: str) -> tuple[str, AxeOSAPI]:
    """Resolve config entry + API client for a given entity_id."""
    entity_registry = er.async_get(hass)
    entity_entry = entity_registry.async_get(entity_id)

    if entity_entry is None:
        raise HomeAssistantError(f"Entity '{entity_id}' not found in entity registry")

    entry_id = entity_entry.config_entry_id
    if not entry_id:
        raise HomeAssistantError(f"Entity '{entity_id}' is not linked to a config entry")

    entry_data = hass.data.get(DOMAIN, {}).get(entry_id)
    if not entry_data:
        raise HomeAssistantError(
            f"No integration data found for entity '{entity_id}' (entry: {entry_id})"
        )

    api = entry_data.get("api")
    if not api:
        raise HomeAssistantError(f"No API client available for entity '{entity_id}'")

    return entry_id, api


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for AxeOS integration."""

    async def handle_restart(call: ServiceCall) -> None:
        """Handle the restart service call."""
        entity_id = call.data["entity_id"]
        entry_id, api = _resolve_api_for_entity(hass, entity_id)

        _LOGGER.info("Restarting miner for %s (entry: %s)", entity_id, entry_id)
        ok = await api.restart_system()
        if not ok:
            raise HomeAssistantError(f"Restart failed for '{entity_id}'")

    async def handle_set_frequency(call: ServiceCall) -> None:
        """Handle the set_frequency service call."""
        entity_id = call.data["entity_id"]
        frequency = call.data["frequency"]
        entry_id, api = _resolve_api_for_entity(hass, entity_id)

        _LOGGER.info(
            "Setting frequency=%s MHz for %s (entry: %s)",
            frequency,
            entity_id,
            entry_id,
        )
        ok = await api.set_frequency(frequency)
        if not ok:
            raise HomeAssistantError(
                f"Setting frequency to {frequency} MHz failed for '{entity_id}'"
            )

    async def handle_set_voltage(call: ServiceCall) -> None:
        """Handle the set_voltage service call."""
        entity_id = call.data["entity_id"]
        voltage = call.data["voltage"]
        entry_id, api = _resolve_api_for_entity(hass, entity_id)

        _LOGGER.info(
            "Setting voltage=%s mV for %s (entry: %s)",
            voltage,
            entity_id,
            entry_id,
        )
        ok = await api.set_voltage(voltage)
        if not ok:
            raise HomeAssistantError(
                f"Setting voltage to {voltage} mV failed for '{entity_id}'"
            )

    hass.services.async_register(
        DOMAIN,
        SERVICE_RESTART,
        handle_restart,
        schema=SERVICE_RESTART_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_FREQUENCY,
        handle_set_frequency,
        schema=SERVICE_SET_FREQUENCY_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_VOLTAGE,
        handle_set_voltage,
        schema=SERVICE_SET_VOLTAGE_SCHEMA,
    )

    _LOGGER.info("AxeOS services registered")


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services."""
    hass.services.async_remove(DOMAIN, SERVICE_RESTART)
    hass.services.async_remove(DOMAIN, SERVICE_SET_FREQUENCY)
    hass.services.async_remove(DOMAIN, SERVICE_SET_VOLTAGE)
    _LOGGER.info("AxeOS services unloaded")
