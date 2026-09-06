"""Tests for AxeOS service actions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.axeos_ha_integration.const import DOMAIN
from custom_components.axeos_ha_integration.models import AxeOSRuntimeData
from custom_components.axeos_ha_integration.services import (
    SERVICE_RESTART,
    SERVICE_SET_FANSPEED,
    SERVICE_SET_FREQUENCY,
    SERVICE_SET_VOLTAGE,
    _resolve_api_for_entity,
    async_setup_services,
    async_unload_services,
)


def make_hass_and_api():
    """Create Home Assistant and API doubles linked through an entity."""
    api = MagicMock()
    api.restart_system = AsyncMock(return_value=True)
    api.set_frequency = AsyncMock(return_value=True)
    api.set_voltage = AsyncMock(return_value=True)
    api.set_fanspeed = AsyncMock(return_value=True)
    hass = MagicMock()
    config_entry = MagicMock()
    config_entry.runtime_data = AxeOSRuntimeData(
        coordinator=MagicMock(), api=api, host="192.0.2.1", name="Miner"
    )
    hass.config_entries.async_get_entry.return_value = config_entry
    hass.services.has_service.return_value = False
    entity_registry = MagicMock()
    entity_registry.async_get.return_value = MagicMock(config_entry_id="entry-id")
    return hass, api, entity_registry


def test_resolve_api_for_entity():
    """Resolve an API instance from an entity registry entry."""
    hass, api, entity_registry = make_hass_and_api()
    with patch(
        "custom_components.axeos_ha_integration.services.er.async_get",
        return_value=entity_registry,
    ):
        entry_id, resolved = _resolve_api_for_entity(hass, "sensor.miner")

    assert entry_id == "entry-id"
    assert resolved is api


@pytest.mark.asyncio
async def test_service_handlers_call_api_and_report_failures():
    """Registered handlers route commands and reject failed operations."""
    hass, api, entity_registry = make_hass_and_api()
    with patch(
        "custom_components.axeos_ha_integration.services.er.async_get",
        return_value=entity_registry,
    ):
        await async_setup_services(hass)

        handlers = {
            call.args[1]: call.args[2]
            for call in hass.services.async_register.call_args_list
        }
        await handlers[SERVICE_RESTART](MagicMock(data={"entity_id": "sensor.miner"}))
        await handlers[SERVICE_SET_FREQUENCY](
            MagicMock(data={"entity_id": "sensor.miner", "frequency": 525})
        )
        await handlers[SERVICE_SET_VOLTAGE](
            MagicMock(data={"entity_id": "sensor.miner", "voltage": 1250})
        )
        await handlers[SERVICE_SET_FANSPEED](
            MagicMock(data={"entity_id": "sensor.miner", "fanspeed": 75})
        )

        api.set_frequency.return_value = False
        with pytest.raises(HomeAssistantError, match="Setting frequency"):
            await handlers[SERVICE_SET_FREQUENCY](
                MagicMock(data={"entity_id": "sensor.miner", "frequency": 500})
            )

    api.restart_system.assert_awaited_once()
    api.set_voltage.assert_awaited_once_with(1250)
    api.set_fanspeed.assert_awaited_once_with(75)


@pytest.mark.asyncio
async def test_unload_services_removes_all_actions():
    """All integration services are removed on final unload."""
    hass = MagicMock()

    await async_unload_services(hass)

    removed = {call.args for call in hass.services.async_remove.call_args_list}
    assert removed == {
        (DOMAIN, SERVICE_RESTART),
        (DOMAIN, SERVICE_SET_FREQUENCY),
        (DOMAIN, SERVICE_SET_VOLTAGE),
        (DOMAIN, SERVICE_SET_FANSPEED),
    }
