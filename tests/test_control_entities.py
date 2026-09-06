"""Tests for writable AxeOS entities."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.axeos_ha_integration.button import AxeOSRestartButton
from custom_components.axeos_ha_integration.number import (
    NUMBER_TYPES,
    AxeOSNumberEntity,
)
from custom_components.axeos_ha_integration.switch import (
    SWITCH_TYPES,
    AxeOSSwitchEntity,
)


@pytest.fixture
def coordinator():
    """Return a coordinator double."""
    coordinator = MagicMock()
    coordinator.data = {"boardVersion": "204", "version": "2.0"}
    coordinator.last_update_success = True
    coordinator.async_request_refresh = AsyncMock()
    return coordinator


@pytest.fixture
def api():
    """Return an API double."""
    api = MagicMock()
    api.restart_system = AsyncMock(return_value=True)
    api.set_fanspeed = AsyncMock(return_value=True)
    api.set_frequency = AsyncMock(return_value=True)
    api.set_voltage = AsyncMock(return_value=True)
    api.set_setting = AsyncMock(return_value=True)
    return api


def make_number(coordinator, api, key="fanspeed"):
    """Create a number entity for a setting."""
    return AxeOSNumberEntity(
        coordinator,
        api,
        "entry-id",
        next(description for description in NUMBER_TYPES if description.key == key),
    )


@pytest.mark.asyncio
async def test_button_uses_coordinator_availability(coordinator, api):
    """The restart button follows current coordinator availability."""
    button = AxeOSRestartButton(coordinator, "entry-id", "Miner", "miner", api)

    assert button.available is True
    coordinator.last_update_success = False
    assert button.available is False


@pytest.mark.asyncio
async def test_button_reports_command_failure(coordinator, api):
    """A failed restart is visible to Home Assistant."""
    api.restart_system.return_value = False
    button = AxeOSRestartButton(coordinator, "entry-id", "Miner", "miner", api)

    with pytest.raises(HomeAssistantError, match="Restart failed"):
        await button.async_press()


@pytest.mark.asyncio
async def test_number_refreshes_after_success(coordinator, api):
    """A successful number command refreshes the coordinator."""
    entity = make_number(coordinator, api)

    await entity.async_set_native_value(75)

    api.set_fanspeed.assert_awaited_once_with(75)
    coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_number_reports_command_failure(coordinator, api):
    """A failed number command is visible to Home Assistant."""
    api.set_fanspeed.return_value = False
    entity = make_number(coordinator, api)

    with pytest.raises(HomeAssistantError, match="Failed to set fanspeed"):
        await entity.async_set_native_value(75)

    coordinator.async_request_refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_switch_reports_command_failure(coordinator, api):
    """A failed switch command is visible to Home Assistant."""
    api.set_setting.return_value = False
    entity = AxeOSSwitchEntity(
        coordinator,
        api,
        "entry-id",
        "miner",
        next(
            description
            for description in SWITCH_TYPES
            if description.key == "autofanspeed"
        ),
    )

    with pytest.raises(HomeAssistantError, match="Failed to enable"):
        await entity.async_turn_on()

    coordinator.async_request_refresh.assert_not_awaited()
