"""Tests for the AxeOS HA Integration binary sensor platform."""
import pytest
from unittest.mock import MagicMock

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import EntityCategory

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
        "shutdown": 0,
        "stratum_keep": True,
        "boardVersion": "204",
        "version": "v2.1.8",
    }
    coordinator.last_update_success = True
    return coordinator


def make_sensor(coordinator, key: str, entry_id: str = "test_entry") -> AxeOSBinarySensor:
    """Create a binary sensor entity from its BINARY_SENSOR_TYPES definition."""
    name, path, device_class, entity_category = BINARY_SENSOR_TYPES[key]
    return AxeOSBinarySensor(
        coordinator,
        entry_id,
        name,
        f"{entry_id}_{key}",
        path,
        key,
        device_class,
        entity_category,
    )


def test_binary_sensor_types_definition():
    """Test that binary sensor types are properly defined."""
    assert "overheat_mode" in BINARY_SENSOR_TYPES
    assert "isUsingFallbackStratum" in BINARY_SENSOR_TYPES

    # Test binary sensor type structure
    overheat_sensor = BINARY_SENSOR_TYPES["overheat_mode"]
    assert len(overheat_sensor) == 4
    assert overheat_sensor[0] == "Overheat Mode"
    assert overheat_sensor[2] == BinarySensorDeviceClass.PROBLEM


def test_get_value_true_values():
    """Test get_value function with various true values."""
    assert get_value({"k": True}, ["k"]) is True
    assert get_value({"k": 1}, ["k"]) is True
    assert get_value({"k": "1"}, ["k"]) is True
    assert get_value({"k": "true"}, ["k"]) is True
    assert get_value({"k": "True"}, ["k"]) is True
    assert get_value({"k": "TRUE"}, ["k"]) is True
    assert get_value({"k": "on"}, ["k"]) is True
    assert get_value({"k": "On"}, ["k"]) is True
    assert get_value({"k": "yes"}, ["k"]) is True


def test_get_value_false_values():
    """Test get_value function with various false values."""
    assert get_value({"k": False}, ["k"]) is False
    assert get_value({"k": 0}, ["k"]) is False
    assert get_value({"k": "0"}, ["k"]) is False
    assert get_value({"k": "false"}, ["k"]) is False
    assert get_value({"k": "False"}, ["k"]) is False
    assert get_value({"k": "off"}, ["k"]) is False
    assert get_value({"k": "no"}, ["k"]) is False


def test_get_value_missing_key():
    """Test get_value function with a missing key."""
    assert get_value({}, ["missing"]) is None


def test_get_value_nested_path():
    """Test get_value function with a nested dotted path."""
    data = {"stratum": {"usingFallback": True}}
    assert get_value(data, ["stratum.usingFallback"]) is True


def test_binary_sensor_is_on(mock_coordinator):
    """Test binary sensor is_on property."""
    sensor = make_sensor(mock_coordinator, "overheat_mode")

    # overheat_mode is 1, should be True
    assert sensor.is_on is True


def test_binary_sensor_is_on_boolean(mock_coordinator):
    """Test binary sensor with boolean value."""
    sensor = make_sensor(mock_coordinator, "isUsingFallbackStratum")

    # isUsingFallbackStratum is False
    assert sensor.is_on is False


def test_binary_sensor_availability(mock_coordinator):
    """Test binary sensor availability."""
    sensor = make_sensor(mock_coordinator, "overheat_mode")

    assert sensor.available is True

    # Test unavailable when coordinator fails
    mock_coordinator.last_update_success = False
    assert sensor.available is False


def test_binary_sensor_missing_data(mock_coordinator):
    """Test binary sensor when data is missing."""
    sensor = make_sensor(mock_coordinator, "otp")

    assert sensor.is_on is None
    assert sensor.available is False


def test_binary_sensor_unique_id(mock_coordinator):
    """Test binary sensor unique ID generation."""
    sensor = make_sensor(mock_coordinator, "overheat_mode", entry_id="test_entry_123")

    assert sensor.unique_id == "test_entry_123_overheat_mode"


def test_binary_sensor_device_info(mock_coordinator):
    """Test binary sensor device info."""
    sensor = make_sensor(mock_coordinator, "overheat_mode", entry_id="test_entry_123")

    device_info = sensor.device_info
    assert device_info is not None
    assert ("axeos_ha_integration", "test_entry_123") in device_info["identifiers"]


def test_binary_sensor_entity_category(mock_coordinator):
    """Test binary sensor entity category."""
    sensor = make_sensor(mock_coordinator, "overheat_mode")

    assert sensor.entity_category == EntityCategory.DIAGNOSTIC


def test_binary_sensor_device_class(mock_coordinator):
    """Test binary sensor device class."""
    sensor = make_sensor(mock_coordinator, "overheat_mode")

    assert sensor.device_class == BinarySensorDeviceClass.PROBLEM
