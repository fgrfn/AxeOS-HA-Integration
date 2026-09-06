"""Tests for config-entry runtime data."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.axeos_ha_integration import async_setup_entry, async_unload_entry
from custom_components.axeos_ha_integration.models import AxeOSRuntimeData
from custom_components.axeos_ha_integration.services import _resolve_api_for_entity


@pytest.mark.asyncio
async def test_setup_stores_typed_runtime_data():
    """Setup stores API and coordinator data on the config entry."""
    hass = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    entry = MagicMock()
    entry.entry_id = "entry-id"
    entry.data = {"host": "192.0.2.1", "name": "Miner", "scan_interval": 30}
    entry.options = {}
    api = MagicMock()
    coordinator = MagicMock()
    coordinator.data = {"boardVersion": "204", "version": "2.0"}
    coordinator.async_config_entry_first_refresh = AsyncMock()

    with (
        patch("custom_components.axeos_ha_integration.async_get_clientsession"),
        patch("custom_components.axeos_ha_integration.AxeOSAPI", return_value=api),
        patch(
            "custom_components.axeos_ha_integration.DataUpdateCoordinator",
            return_value=coordinator,
        ),
        patch("custom_components.axeos_ha_integration.dr.async_get"),
        patch(
            "custom_components.axeos_ha_integration.async_setup_services",
            new=AsyncMock(),
        ),
    ):
        assert await async_setup_entry(hass, entry) is True

    assert isinstance(entry.runtime_data, AxeOSRuntimeData)
    assert entry.runtime_data.api is api
    assert entry.runtime_data.coordinator is coordinator
    assert entry.runtime_data.host == "192.0.2.1"


def test_service_resolution_uses_config_entry_runtime_data():
    """Service routing resolves the API from config-entry runtime data."""
    api = MagicMock()
    config_entry = MagicMock()
    config_entry.runtime_data = AxeOSRuntimeData(
        coordinator=MagicMock(), api=api, host="192.0.2.1", name="Miner"
    )
    hass = MagicMock()
    hass.config_entries.async_get_entry.return_value = config_entry
    entity_registry = MagicMock()
    entity_registry.async_get.return_value = MagicMock(config_entry_id="entry-id")

    with patch(
        "custom_components.axeos_ha_integration.services.er.async_get",
        return_value=entity_registry,
    ):
        entry_id, resolved_api = _resolve_api_for_entity(hass, "sensor.miner")

    assert entry_id == "entry-id"
    assert resolved_api is api


@pytest.mark.asyncio
async def test_unload_last_runtime_entry_removes_services():
    """The final loaded entry removes shared services."""
    hass = MagicMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.config_entries.async_loaded_entries.return_value = [MagicMock()]
    entry = MagicMock(entry_id="entry-id")

    with patch(
        "custom_components.axeos_ha_integration.async_unload_services",
        new=AsyncMock(),
    ) as unload_services:
        assert await async_unload_entry(hass, entry) is True

    unload_services.assert_awaited_once_with(hass)
