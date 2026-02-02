"""Tests for the AxeOS HA Integration API."""
import pytest
from aiohttp import ClientSession
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.axeos_ha_integration.api import AxeOSAPI


@pytest.fixture
def mock_session():
    """Create a mock aiohttp ClientSession."""
    return MagicMock(spec=ClientSession)


@pytest.fixture
def api(mock_session):
    """Create an AxeOSAPI instance with mock session."""
    return AxeOSAPI(mock_session, "192.168.1.100")


@pytest.mark.asyncio
async def test_get_system_info_success(api, mock_session):
    """Test successful system info retrieval."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "power": 12.5,
        "voltage": 5000,
        "current": 2500,
        "temp": 45.5,
        "hashRate": 500.0,
    })
    
    mock_session.get = AsyncMock(return_value=mock_response)
    
    result = await api.get_system_info()
    
    assert result is not None
    assert result["power"] == 12.5
    assert result["temp"] == 45.5
    assert result["hashRate"] == 500.0
    mock_session.get.assert_called_once_with("http://192.168.1.100/api/system/info")


@pytest.mark.asyncio
async def test_get_system_info_failure(api, mock_session):
    """Test system info retrieval failure."""
    mock_response = AsyncMock()
    mock_response.status = 404
    
    mock_session.get = AsyncMock(return_value=mock_response)
    
    result = await api.get_system_info()
    
    assert result is None


@pytest.mark.asyncio
async def test_restart_system_success(api, mock_session):
    """Test successful system restart."""
    mock_response = AsyncMock()
    mock_response.status = 200
    
    mock_session.post = AsyncMock(return_value=mock_response)
    
    result = await api.restart_system()
    
    assert result is True
    mock_session.post.assert_called_once_with("http://192.168.1.100/api/system/restart")


@pytest.mark.asyncio
async def test_restart_system_failure(api, mock_session):
    """Test system restart failure."""
    mock_response = AsyncMock()
    mock_response.status = 500
    
    mock_session.post = AsyncMock(return_value=mock_response)
    
    result = await api.restart_system()
    
    assert result is False


@pytest.mark.asyncio
async def test_set_frequency_success(api, mock_session):
    """Test setting frequency successfully."""
    mock_response = AsyncMock()
    mock_response.status = 200
    
    mock_session.post = AsyncMock(return_value=mock_response)
    
    result = await api.set_frequency(500)
    
    assert result is True
    mock_session.post.assert_called_once_with(
        "http://192.168.1.100/api/system/frequency",
        json={"frequency": 500}
    )


@pytest.mark.asyncio
async def test_set_voltage_success(api, mock_session):
    """Test setting voltage successfully."""
    mock_response = AsyncMock()
    mock_response.status = 200
    
    mock_session.post = AsyncMock(return_value=mock_response)
    
    result = await api.set_voltage(1200)
    
    assert result is True
    mock_session.post.assert_called_once_with(
        "http://192.168.1.100/api/system/voltage",
        json={"voltage": 1200}
    )


@pytest.mark.asyncio
async def test_set_fanspeed_success(api, mock_session):
    """Test setting fan speed successfully."""
    mock_response = AsyncMock()
    mock_response.status = 200
    
    mock_session.post = AsyncMock(return_value=mock_response)
    
    result = await api.set_fanspeed(75)
    
    assert result is True
    mock_session.post.assert_called_once_with(
        "http://192.168.1.100/api/system/fanspeed",
        json={"fanspeed": 75}
    )


@pytest.mark.asyncio
async def test_host_with_protocol(mock_session):
    """Test that protocol is stripped from host."""
    api = AxeOSAPI(mock_session, "http://192.168.1.100")
    
    assert api.host == "192.168.1.100"
