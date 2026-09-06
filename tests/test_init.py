"""Tests for integration setup and unload."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.axeos_ha_integration import async_setup_entry, async_unload_entry
from custom_components.axeos_ha_integration.const import DOMAIN


@pytest.mark.asyncio
async def test_setup_entry_initializes_coordinator_and_platforms():
    """A config entry initializes its API, coordinator, device, and platforms."""
    hass = MagicMock()
    hass.data = {}
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_reload = AsyncMock()
    entry = MagicMock()
    entry.entry_id = "entry-id"
    entry.data = {"host": "192.0.2.1", "name": "Miner", "scan_interval": 30}
    entry.options = {}
    entry.add_update_listener.return_value = MagicMock()

    api = MagicMock()
    api.get_system_info = AsyncMock(return_value={"hashRate": 500})
    coordinator = MagicMock()
    coordinator.data = {"boardVersion": "204", "version": "2.0"}
    coordinator.async_config_entry_first_refresh = AsyncMock()
    device_registry = MagicMock()

    with (
        patch(
            "custom_components.axeos_ha_integration.async_get_clientsession"
        ) as get_session,
        patch(
            "custom_components.axeos_ha_integration.AxeOSAPI", return_value=api
        ),
        patch(
            "custom_components.axeos_ha_integration.DataUpdateCoordinator",
            return_value=coordinator,
        ) as coordinator_class,
        patch(
            "custom_components.axeos_ha_integration.dr.async_get",
            return_value=device_registry,
        ),
        patch(
            "custom_components.axeos_ha_integration.async_setup_services",
            new=AsyncMock(),
        ) as setup_services,
    ):
        assert await async_setup_entry(hass, entry) is True

    get_session.assert_called_once_with(hass)
    coordinator.async_config_entry_first_refresh.assert_awaited_once()
    hass.config_entries.async_forward_entry_setups.assert_awaited_once()
    setup_services.assert_awaited_once_with(hass)
    entry.async_on_unload.assert_called_once()
    assert hass.data[DOMAIN]["entry-id"]["api"] is api

    update_method = coordinator_class.call_args.kwargs["update_method"]
    data = await update_method()
    assert data["hashrate_history"] == [500]


@pytest.mark.asyncio
async def test_unload_last_entry_removes_services():
    """Unloading the final entry removes shared services."""
    hass = MagicMock()
    hass.data = {DOMAIN: {"entry-id": {}}}
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    entry = MagicMock(entry_id="entry-id")

    with patch(
        "custom_components.axeos_ha_integration.async_unload_services",
        new=AsyncMock(),
    ) as unload_services:
        assert await async_unload_entry(hass, entry) is True

    unload_services.assert_awaited_once_with(hass)
    assert hass.data[DOMAIN] == {}
