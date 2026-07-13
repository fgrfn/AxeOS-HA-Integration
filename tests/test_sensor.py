"""Tests for the AxeOS HA Integration sensor platform."""
import pytest
from unittest.mock import MagicMock, patch

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import EntityCategory

from custom_components.axeos_ha_integration.sensor import (
    SENSOR_TYPES,
    AxeOSHASensor,
    get_value,
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
        "boardVersion": "204",
        "version": "v2.1.8",
    }
    coordinator.last_update_success = True
    return coordinator


def make_sensor(coordinator, key: str, entry_id: str = "test_entry") -> AxeOSHASensor:
    """Create a sensor entity from its SENSOR_TYPES definition."""
    name, unit, path, device_class, state_class, entity_category = SENSOR_TYPES[key]
    return AxeOSHASensor(
        coordinator,
        entry_id,
        name,
        f"{entry_id}_{key}",
        unit,
        path,
        key,
        device_class,
        state_class,
        entity_category,
    )


def refresh(sensor: AxeOSHASensor) -> None:
    """Trigger a coordinator update without a hass instance."""
    with patch.object(sensor, "async_write_ha_state"):
        sensor._handle_coordinator_update()


def test_sensor_types_definition():
    """Test that sensor types are properly defined."""
    assert "power" in SENSOR_TYPES
    assert "voltage" in SENSOR_TYPES
    assert "temp" in SENSOR_TYPES
    assert "hashRate" in SENSOR_TYPES

    # Test sensor type structure
    power_sensor = SENSOR_TYPES["power"]
    assert len(power_sensor) == 6  # 6 elements in tuple
    assert power_sensor[0] == "Power Consumption"
    assert power_sensor[1] == "W"
    assert power_sensor[2] == ["power"]
    assert power_sensor[3] == SensorDeviceClass.POWER
    assert power_sensor[4] == SensorStateClass.MEASUREMENT


def test_get_value_flat_key():
    """Test get_value with a plain key."""
    assert get_value({"power": 12.5}, ["power"]) == 12.5


def test_get_value_alternative_keys():
    """Test get_value trying alternative keys."""
    assert get_value({"hostip": "1.2.3.4"}, ["ip", "hostip"]) == "1.2.3.4"


def test_get_value_nested_path():
    """Test get_value following a nested path."""
    data = {"stratum": {"poolMode": "solo"}}
    assert get_value(data, ["stratum", "poolMode"]) == "solo"


def test_get_value_missing():
    """Test get_value with a missing key."""
    assert get_value({"power": 12.5}, ["nonexistent"]) is None
    assert get_value({}, []) is None


def test_sensor_native_value(mock_coordinator):
    """Test sensor native value after a coordinator update."""
    sensor = make_sensor(mock_coordinator, "power")
    refresh(sensor)

    assert sensor.native_value == 12.5


def test_sensor_availability(mock_coordinator):
    """Test sensor availability."""
    sensor = make_sensor(mock_coordinator, "power")
    refresh(sensor)

    assert sensor.available is True

    # Test unavailable when coordinator fails
    mock_coordinator.last_update_success = False
    assert sensor.available is False


def test_sensor_missing_data(mock_coordinator):
    """Test sensor when data is missing."""
    sensor = make_sensor(mock_coordinator, "ssid")
    refresh(sensor)

    assert sensor.native_value is None
    assert sensor.available is False


def test_sensor_unique_id(mock_coordinator):
    """Test sensor unique ID generation."""
    sensor = make_sensor(mock_coordinator, "power", entry_id="test_entry_123")

    assert sensor.unique_id == "test_entry_123_power"


def test_sensor_unit(mock_coordinator):
    """Test sensor unit of measurement."""
    sensor = make_sensor(mock_coordinator, "power")

    assert sensor.native_unit_of_measurement == "W"


def test_sensor_device_info(mock_coordinator):
    """Test sensor device info."""
    sensor = make_sensor(mock_coordinator, "power", entry_id="test_entry_123")

    device_info = sensor.device_info
    assert device_info is not None
    assert ("axeos_ha_integration", "test_entry_123") in device_info["identifiers"]


def test_sensor_display_precision(mock_coordinator):
    """Test sensor display precision."""
    sensor = make_sensor(mock_coordinator, "power")

    assert sensor.suggested_display_precision == 2

    hashrate_sensor = make_sensor(mock_coordinator, "hashRate")
    assert hashrate_sensor.suggested_display_precision == 0


def test_sensor_entity_category(mock_coordinator):
    """Test sensor entity category."""
    # uptimeSeconds is a diagnostic sensor
    sensor = make_sensor(mock_coordinator, "uptimeSeconds")

    assert sensor.entity_category == EntityCategory.DIAGNOSTIC

    # power is a regular sensor
    power_sensor = make_sensor(mock_coordinator, "power")
    assert power_sensor.entity_category is None


def test_sensor_hashrate_history_attributes(mock_coordinator):
    """Test hashrate history attributes on the hashRate sensor."""
    mock_coordinator.data["hashrate_history"] = [400.0, 500.0, 600.0]
    sensor = make_sensor(mock_coordinator, "hashRate")

    attrs = sensor.extra_state_attributes
    assert attrs["hashrate_min"] == 400.0
    assert attrs["hashrate_max"] == 600.0
    assert attrs["hashrate_avg"] == 500.0
