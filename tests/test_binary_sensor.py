"""Tests for the AxeOS HA Integration binary sensor platform."""
import pytest
from unittest.mock import MagicMock

from custom_components.axeos_ha_integration.binary_sensor import (
    BINARY_SENSOR_TYPES,
    AxeOSBinarySensor,
    get_value,
)


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "overheat_mode": 1,
        "isUsingFallbackStratum": False,
        "autofanspeed": True,
        "invertfanpolarity": 0,
        "flipscreen": 1,
        "invertscreen": False,
    }
    coordinator.last_update_success = True
    return coordinator


def test_binary_sensor_types_definition():
    """Test that binary sensor types are properly defined."""
    assert "overheat_mode" in BINARY_SENSOR_TYPES
    assert "isUsingFallbackStratum" in BINARY_SENSOR_TYPES
    assert "autofanspeed" in BINARY_SENSOR_TYPES
    
    # Test binary sensor type structure
    overheat_sensor = BINARY_SENSOR_TYPES["overheat_mode"]
    assert len(overheat_sensor) == 3
    assert overheat_sensor[0] == "Overheat Mode"


def test_get_value_true_values():
    """Test get_value function with various true values."""
    assert get_value(True) is True
    assert get_value(1) is True
    assert get_value("1") is True
    assert get_value("true") is True
    assert get_value("True") is True
    assert get_value("TRUE") is True
    assert get_value("on") is True
    assert get_value("On") is True
    assert get_value("yes") is True


def test_get_value_false_values():
    """Test get_value function with various false values."""
    assert get_value(False) is False
    assert get_value(0) is False
    assert get_value("0") is False
    assert get_value("false") is False
    assert get_value("False") is False
    assert get_value("off") is False
    assert get_value("no") is False
    assert get_value(None) is False


def test_binary_sensor_is_on(mock_coordinator):
    """Test binary sensor is_on property."""
    sensor = AxeOSBinarySensor(
        mock_coordinator,
        "test_entry",
        "overheat_mode",
        "Overheat Mode",
        "overheat_mode",
        "mdi:fire",
    )
    
    # overheat_mode is 1, should be True
    assert sensor.is_on is True


def test_binary_sensor_is_on_boolean(mock_coordinator):
    """Test binary sensor with boolean value."""
    sensor = AxeOSBinarySensor(
        mock_coordinator,
        "test_entry",
        "isUsingFallbackStratum",
        "Fallback Stratum",
        "isUsingFallbackStratum",
        "mdi:server-network",
    )
    
    # isUsingFallbackStratum is False
    assert sensor.is_on is False


def test_binary_sensor_availability(mock_coordinator):
    """Test binary sensor availability."""
    sensor = AxeOSBinarySensor(
        mock_coordinator,
        "test_entry",
        "autofanspeed",
        "Auto Fan Speed",
        "autofanspeed",
        "mdi:fan-auto",
    )
    
    assert sensor.available is True
    
    # Test unavailable when coordinator fails
    mock_coordinator.last_update_success = False
    assert sensor.available is False


def test_binary_sensor_missing_data(mock_coordinator):
    """Test binary sensor when data is missing."""
    sensor = AxeOSBinarySensor(
        mock_coordinator,
        "test_entry",
        "missing_key",
        "Missing",
        "nonexistent_key",
        "mdi:help",
    )
    
    assert sensor.is_on is False


def test_binary_sensor_unique_id(mock_coordinator):
    """Test binary sensor unique ID generation."""
    sensor = AxeOSBinarySensor(
        mock_coordinator,
        "test_entry_123",
        "overheat_mode",
        "Overheat Mode",
        "overheat_mode",
        "mdi:fire",
    )
    
    assert sensor.unique_id == "test_entry_123_overheat_mode"


def test_binary_sensor_device_info(mock_coordinator):
    """Test binary sensor device info."""
    sensor = AxeOSBinarySensor(
        mock_coordinator,
        "test_entry_123",
        "overheat_mode",
        "Overheat Mode",
        "overheat_mode",
        "mdi:fire",
    )
    
    device_info = sensor.device_info
    assert device_info is not None
    assert ("axeos_ha_integration", "test_entry_123") in device_info["identifiers"]


def test_binary_sensor_entity_category(mock_coordinator):
    """Test binary sensor entity category."""
    sensor = AxeOSBinarySensor(
        mock_coordinator,
        "test_entry",
        "overheat_mode",
        "Overheat Mode",
        "overheat_mode",
        "mdi:fire",
    )
    
    assert sensor.entity_category == "diagnostic"


def test_binary_sensor_icon(mock_coordinator):
    """Test binary sensor icon."""
    sensor = AxeOSBinarySensor(
        mock_coordinator,
        "test_entry",
        "autofanspeed",
        "Auto Fan Speed",
        "autofanspeed",
        "mdi:fan-auto",
    )
    
    assert sensor.icon == "mdi:fan-auto"
