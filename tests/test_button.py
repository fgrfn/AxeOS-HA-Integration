"""Tests for the AxeOS restart button."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.axeos_ha_integration.button import async_setup_entry
from custom_components.axeos_ha_integration.const import DOMAIN


@pytest.mark.asyncio
async def test_button_setup_press_and_availability():
    """Set up the button and send a restart command."""
    api = MagicMock()
    api.system_info = {"boardVersion": "204", "version": "2.0"}
    api.restart_system = AsyncMock(return_value=True)
    hass = MagicMock()
    hass.data = {
        DOMAIN: {
            "entry-id": {
                "api": api,
                "name": "Miner",
                "host": "192.0.2.1",
            }
        }
    }
    entry = MagicMock(entry_id="entry-id")
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)

    button = async_add_entities.call_args.args[0][0]
    assert button.available is True
    assert button.device_info["model"] == "204"
    await button.async_press()
    api.restart_system.assert_awaited_once()

    api.system_info = {}
    assert button.available is False
