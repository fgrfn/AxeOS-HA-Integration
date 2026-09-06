"""Tests for the AxeOS config and options flows."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.axeos_ha_integration.config_flow import (
    AxeOSHaIntegrationConfigFlow,
    AxeOSOptionsFlowHandler,
)


@pytest.mark.asyncio
async def test_config_flow_shows_initial_form():
    """The user step displays a form before input."""
    flow = AxeOSHaIntegrationConfigFlow()
    flow.async_show_form = MagicMock(return_value={"type": "form"})

    assert await flow.async_step_user() == {"type": "form"}


@pytest.mark.asyncio
async def test_config_flow_creates_entry_after_probe():
    """A reachable miner creates a config entry."""
    flow = AxeOSHaIntegrationConfigFlow()
    flow.hass = MagicMock()
    flow._async_abort_entries_match = MagicMock()
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
    api = MagicMock()
    api.get_system_info = AsyncMock(return_value={"boardVersion": "204"})

    with (
        patch(
            "custom_components.axeos_ha_integration.config_flow.async_get_clientsession"
        ),
        patch(
            "custom_components.axeos_ha_integration.config_flow.AxeOSAPI",
            return_value=api,
        ),
    ):
        result = await flow.async_step_user(
            {"host": "192.0.2.1", "name": "Miner", "scan_interval": 30}
        )

    assert result == {"type": "create_entry"}
    flow._async_abort_entries_match.assert_called_once_with({"host": "192.0.2.1"})


@pytest.mark.asyncio
async def test_config_flow_rejects_empty_host():
    """An empty host produces a validation error."""
    flow = AxeOSHaIntegrationConfigFlow()
    flow.async_show_form = MagicMock(return_value={"type": "form"})

    await flow.async_step_user({"host": " ", "name": "Miner", "scan_interval": 30})

    assert flow.async_show_form.call_args.kwargs["errors"] == {"host": "invalid_host"}


@pytest.mark.asyncio
async def test_options_flow_reads_and_updates_options():
    """The options flow exposes defaults and saves submitted values."""
    handler = AxeOSOptionsFlowHandler(SimpleNamespace(options={"scan_interval": 60}))
    handler.async_show_form = MagicMock(return_value={"type": "form"})
    handler.async_create_entry = MagicMock(return_value={"type": "create_entry"})

    assert await handler.async_step_init() == {"type": "form"}
    result = await handler.async_step_init({"scan_interval": 45})

    assert result == {"type": "create_entry"}
