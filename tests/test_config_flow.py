"""Tests for the AxeOS config and options flows."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import voluptuous as vol

from custom_components.axeos_ha_integration.config_flow import (
    STEP_USER_DATA_SCHEMA,
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
    api.host = "192.0.2.1"
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
async def test_config_flow_stores_normalized_host():
    """Equivalent host spellings cannot create duplicate config entries."""
    flow = AxeOSHaIntegrationConfigFlow()
    flow.hass = MagicMock()
    flow._async_abort_entries_match = MagicMock()
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
    api = MagicMock()
    api.host = "miner.local"
    api.get_system_info = AsyncMock(return_value={"boardVersion": "204"})

    with (
        patch("custom_components.axeos_ha_integration.config_flow.async_get_clientsession"),
        patch(
            "custom_components.axeos_ha_integration.config_flow.AxeOSAPI",
            return_value=api,
        ),
    ):
        result = await flow.async_step_user(
            {"host": "http://miner.local/", "name": "", "scan_interval": 30}
        )

    assert result == {"type": "create_entry"}
    flow._async_abort_entries_match.assert_called_once_with({"host": "miner.local"})
    assert flow.async_create_entry.call_args.kwargs["data"]["host"] == "miner.local"


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


def test_config_flow_rejects_non_positive_scan_intervals():
    """Polling must not create a zero-delay coordinator update loop."""
    for value in (0, -1):
        with pytest.raises(vol.Invalid):
            STEP_USER_DATA_SCHEMA({"host": "miner.local", "scan_interval": value})


@pytest.mark.asyncio
async def test_options_flow_rejects_non_positive_scan_intervals():
    """Options use the same positive scan-interval constraint."""
    handler = AxeOSOptionsFlowHandler(SimpleNamespace(options={}))
    handler.async_show_form = MagicMock(return_value={"type": "form"})

    await handler.async_step_init()
    schema = handler.async_show_form.call_args.kwargs["data_schema"]

    with pytest.raises(vol.Invalid):
        schema({"scan_interval": 0})
