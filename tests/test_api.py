"""Tests for the AxeOS HA Integration API."""

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
from aiohttp import ClientSession

from custom_components.axeos_ha_integration.api import AxeOSAPI, AxeOSApiError


@pytest.fixture
def mock_session():
    """Create a mock aiohttp ClientSession."""
    return MagicMock(spec=ClientSession)


@pytest.fixture
def api(mock_session):
    """Create an AxeOSAPI instance with mock session."""
    return AxeOSAPI(mock_session, "192.168.1.100")


def prepare_response(mock_session, status=200, payload=None):
    """Prepare an async response context manager."""
    response = MagicMock()
    response.status = status
    response.json = AsyncMock(return_value=payload)
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=response)
    context.__aexit__ = AsyncMock(return_value=None)
    mock_session.request = MagicMock(return_value=context)
    return context, response


@pytest.mark.asyncio
async def test_get_system_info_success(api, mock_session):
    """Test successful system info retrieval."""
    context, _ = prepare_response(
        mock_session,
        payload={
            "power": 12.5,
            "voltage": 5000,
            "current": 2500,
            "temp": 45.5,
            "hashRate": 500.0,
        },
    )

    result = await api.get_system_info()

    assert result is not None
    assert result["power"] == 12.5
    assert result["temp"] == 45.5
    assert result["hashRate"] == 500.0
    mock_session.request.assert_called_once_with(
        "GET", "http://192.168.1.100/api/system/info", json=None
    )
    context.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_system_info_failure(api, mock_session):
    """Test system info retrieval failure."""
    prepare_response(mock_session, status=404)

    with pytest.raises(AxeOSApiError, match="HTTP 404"):
        await api.get_system_info()


@pytest.mark.asyncio
async def test_restart_system_success(api, mock_session):
    """Test successful system restart."""
    prepare_response(mock_session)

    result = await api.restart_system()

    assert result is True
    mock_session.request.assert_called_once_with(
        "POST", "http://192.168.1.100/api/system/restart", json=None
    )


@pytest.mark.asyncio
async def test_restart_system_failure(api, mock_session):
    """Test system restart failure."""
    prepare_response(mock_session, status=500)

    with pytest.raises(AxeOSApiError, match="HTTP 500"):
        await api.restart_system()


@pytest.mark.asyncio
async def test_set_frequency_success(api, mock_session):
    """Test setting frequency successfully."""
    prepare_response(mock_session)

    result = await api.set_frequency(500)

    assert result is True
    mock_session.request.assert_called_once_with(
        "POST",
        "http://192.168.1.100/api/system/frequency",
        json={"frequency": 500},
    )


@pytest.mark.asyncio
async def test_set_voltage_success(api, mock_session):
    """Test setting voltage successfully."""
    prepare_response(mock_session)

    result = await api.set_voltage(1200)

    assert result is True
    mock_session.request.assert_called_once_with(
        "POST",
        "http://192.168.1.100/api/system/voltage",
        json={"voltage": 1200},
    )


@pytest.mark.asyncio
async def test_set_fanspeed_success(api, mock_session):
    """Test setting fan speed successfully."""
    prepare_response(mock_session)

    result = await api.set_fanspeed(75)

    assert result is True
    mock_session.request.assert_called_once_with(
        "POST",
        "http://192.168.1.100/api/system/fanspeed",
        json={"fanspeed": 75},
    )


@pytest.mark.asyncio
async def test_invalid_json_raises_api_error(api, mock_session):
    """Test invalid JSON is reported to the caller."""
    _, response = prepare_response(mock_session)
    response.json.side_effect = ValueError("invalid json")

    with pytest.raises(AxeOSApiError, match="invalid JSON"):
        await api.get_system_info()


@pytest.mark.asyncio
async def test_client_error_raises_api_error(api, mock_session):
    """Test connection errors are reported to the caller."""
    mock_session.request = MagicMock(side_effect=aiohttp.ClientError("offline"))

    with pytest.raises(AxeOSApiError, match="offline"):
        await api.get_system_info()


@pytest.mark.asyncio
async def test_host_with_protocol(mock_session):
    """Test that protocol is stripped from host."""
    api = AxeOSAPI(mock_session, "http://192.168.1.100")

    assert api.host == "192.168.1.100"
