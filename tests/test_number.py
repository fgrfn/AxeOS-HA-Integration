"""Tests for AxeOS number entities."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.axeos_ha_integration.const import DOMAIN
from custom_components.axeos_ha_integration.number import async_setup_entry


@pytest.mark.asyncio
async def test_number_setup_values_and_commands():
    """Set up all number entities and exercise their commands."""
    coordinator = MagicMock()
    coordinator.data = {"fanspeed": 50, "frequency": 500, "coreVoltage": 1200}
    coordinator.last_update_success = True
    coordinator.async_request_refresh = AsyncMock()
    api = MagicMock()
    api.set_fanspeed = AsyncMock(return_value=True)
    api.set_frequency = AsyncMock(return_value=True)
    api.set_voltage = AsyncMock(return_value=True)
    hass = MagicMock()
    hass.data = {DOMAIN: {"entry-id": {"coordinator": coordinator, "api": api}}}
    entry = MagicMock(entry_id="entry-id")
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)

    entities = async_add_entities.call_args.args[0]
    assert len(entities) == 3
    by_key = {entity._key: entity for entity in entities}
    assert by_key["fanspeed"].native_value == 50
    assert by_key["fanspeed"].available is True

    await by_key["fanspeed"].async_set_native_value(75)
    await by_key["frequency"].async_set_native_value(525)
    await by_key["coreVoltage"].async_set_native_value(1250)

    api.set_fanspeed.assert_awaited_once_with(75)
    api.set_frequency.assert_awaited_once_with(525)
    api.set_voltage.assert_awaited_once_with(1250)
    assert coordinator.async_request_refresh.await_count == 3
