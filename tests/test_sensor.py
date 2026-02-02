"""Tests for the AxeOS HA Integration sensor platform."""
import pytest
from unittest.mock import MagicMock
from homeassistant.const import UnitOfPower, UnitOfElectricPotential, UnitOfElectricCurrent

from custom_components.axeos_ha_integration.sensor import (
    SENSOR_TYPES,
    AxeOSSensor,
)


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "power": 12.5,
        "voltage": 5000,
        "current": 2500,
        "temp": 45.5,
        "hashRate": 500.0,
        "bestDiff": "1234",
        "bestSessionDiff": "5678",
        "uptimeSeconds": 3600,
        "frequency": 485,
        "coreVoltage": 1250,
        "fanspeed": 75,
    }
    coordinator.last_update_success = True
    return coordinator


def test_sensor_types_definition():
    """Test that sensor types are properly defined."""
    assert "power" in SENSOR_TYPES
    assert "voltage" in SENSOR_TYPES
    assert "temp" in SENSOR_TYPES
    assert "hashRate" in SENSOR_TYPES
    
    # Test sensor type structure
    power_sensor = SENSOR_TYPES["power"]
    assert len(power_sensor) == 7  # 7 elements in tuple
    assert power_sensor[0] == "Power"
    assert power_sensor[1] == UnitOfPower.WATT


def test_sensor_native_value(mock_coordinator):
    """Test sensor native value property."""
    sensor = AxeOSSensor(
        mock_coordinator,
        "test_entry",
        "power",
        "Power",
        UnitOfPower.WATT,
        "power",
        "power",
        "measurement",
        None,
        2,
    )
    
    assert sensor.native_value == 12.5


def test_sensor_availability(mock_coordinator):
    """Test sensor availability."""
    sensor = AxeOSSensor(
        mock_coordinator,
        "test_entry",
        "power",
        "Power",
        UnitOfPower.WATT,
        "power",
        "power",
        "measurement",
        None,
        2,
    )
    
    assert sensor.available is True
    
    # Test unavailable when coordinator fails
    mock_coordinator.last_update_success = False
    assert sensor.available is False


def test_sensor_nested_data_path(mock_coordinator):
    """Test sensor with nested data path."""
    mock_coordinator.data["wifi"] = {"status": "Connected"}
    
    sensor = AxeOSSensor(
        mock_coordinator,
        "test_entry",
        "wifi_status",
        "WiFi Status",
        None,
        "wifi.status",
        None,
        None,
        None,
        None,
    )
    
    assert sensor.native_value == "Connected"


def test_sensor_missing_data(mock_coordinator):
    """Test sensor when data is missing."""
    sensor = AxeOSSensor(
        mock_coordinator,
        "test_entry",
        "missing_key",
        "Missing",
        None,
        "nonexistent_key",
        None,
        None,
        None,
        None,
    )
    
    assert sensor.native_value is None


def test_sensor_unique_id(mock_coordinator):
    """Test sensor unique ID generation."""
    sensor = AxeOSSensor(
        mock_coordinator,
        "test_entry_123",
        "power",
        "Power",
        UnitOfPower.WATT,
        "power",
        "power",
        "measurement",
        None,
        2,
    )
    
    assert sensor.unique_id == "test_entry_123_power"


def test_sensor_device_info(mock_coordinator):
    """Test sensor device info."""
    sensor = AxeOSSensor(
        mock_coordinator,
        "test_entry_123",
        "power",
        "Power",
        UnitOfPower.WATT,
        "power",
        "power",
        "measurement",
        None,
        2,
    )
    
    device_info = sensor.device_info
    assert device_info is not None
    assert ("axeos_ha_integration", "test_entry_123") in device_info["identifiers"]


def test_sensor_display_precision(mock_coordinator):
    """Test sensor display precision."""
    sensor = AxeOSSensor(
        mock_coordinator,
        "test_entry",
        "power",
        "Power",
        UnitOfPower.WATT,
        "power",
        "power",
        "measurement",
        None,
        2,  # 2 decimal places
    )
    
    assert sensor.suggested_display_precision == 2


def test_sensor_entity_category(mock_coordinator):
    """Test sensor entity category."""
    # Test diagnostic sensor
    sensor = AxeOSSensor(
        mock_coordinator,
        "test_entry",
        "uptimeSeconds",
        "Uptime",
        "s",
        "uptimeSeconds",
        None,
        None,
        "diagnostic",
        None,
    )
    
    assert sensor.entity_category == "diagnostic"
