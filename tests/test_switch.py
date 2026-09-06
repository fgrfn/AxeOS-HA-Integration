"""Tests for AxeOS switch entities."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.axeos_ha_integration.const import DOMAIN
from custom_components.axeos_ha_integration.switch import async_setup_entry


@pytest.mark.asyncio
async def test_switch_setup_states_and_commands():
    """Set up switches, decode states, and send commands."""
    coordinator = MagicMock()
    coordinator.data = {
        "autofanspeed": "on",
        "invertfanpolarity": 0,
        "flipscreen": True,
        "invertscreen": "false",
        "autoscreenoff": 1,
    }
    coordinator.last_update_success = True
    coordinator.async_request_refresh = AsyncMock()
    api = MagicMock()
    api.set_setting = AsyncMock(return_value=True)
    hass = MagicMock()
    hass.data = {DOMAIN: {"entry-id": {"coordinator": coordinator, "api": api}}}
    entry = MagicMock(entry_id="entry-id")
    entry.data = {"host": "192.0.2.1"}
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)

    entities = async_add_entities.call_args.args[0]
    by_key = {entity._key: entity for entity in entities}
    assert by_key["autofanspeed"].is_on is True
    assert by_key["invertfanpolarity"].is_on is False
    assert by_key["autofanspeed"].available is True

    await by_key["autofanspeed"].async_turn_off()
    await by_key["autofanspeed"].async_turn_on()

    assert api.set_setting.await_args_list[0].args == ("autofanspeed", False)
    assert api.set_setting.await_args_list[1].args == ("autofanspeed", True)
    assert coordinator.async_request_refresh.await_count == 2
