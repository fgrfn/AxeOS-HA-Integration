# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.8] - 2025-02-03

### Added
- Full NerdAxe device support with 25+ additional sensors
- Extended hashrate metrics (1 minute, 10 minutes, 1 hour, 1 day averages)
- Min/Max power and voltage sensors for NerdAxe
- PID controller value sensors (P, I, D values and target temperature)
- Stratum pool details (pool mode, balance, total best difficulty)
- Additional fan control (manual fan speed, fan RPM)
- Hardware diagnostics (duplicate nonces, found blocks, reset reason)
- VR frequency monitoring and configuration
- Nested data path support for complex API structures

### Improved
- IP address sensor now supports both "ip" and "hostip" fields
- Binary sensors support nested paths (e.g., stratum.usingFallback)
- Better compatibility with both BitAxe and NerdAxe devices
- Enhanced get_value() functions for nested data extraction

## [1.0.7] - 2025-02-03

### Added
- Number entities for editable values (fan speed, frequency, core voltage)
- Custom services (restart_miner, set_frequency, set_voltage)
- Unit tests for API, sensors, and binary sensors
- Service definitions with proper UI selectors in services.yaml
- Test documentation in tests/README.md

### Improved
- Services are now properly registered and unloaded with the integration
- API methods for setting frequency, voltage, and fan speed
- Better code coverage with pytest test suite

## [1.0.1] - 2026-02-02

## [1.0.0] - 2026-02-02

### Added
- Hide temperature sensors option in configuration
- Update listener for options changes (scan interval, logging level, hide sensors)
- info.md for HACS integration sidebar
- LICENSE file (MIT)
- Proper .gitignore file
- This CHANGELOG.md

### Fixed
- Missing `sensor_key` property in sensor entity causing AttributeError
- Missing `restart_system()` method in AxeOSAPI class
- Duplicate AxeOSAPI class definition in button.py
- Scan interval now properly uses options instead of config data
- Options flow now triggers integration reload on change

### Changed
- Moved duplicate files from root to proper location in custom_components
- Repository structure now fully HACS-compatible
- Improved error handling in API restart method

## [1.0.4] - 2025-07-16

### Added
- Connection Status Sensor showing online/offline state
- Historical Statistics with min/max/average hashrate as attributes
- Advanced UI Options for scan interval and logging level
- Diagnostic Attributes showing last error and rejected share reasons
- Multi-Miner Support for managing multiple miners independently
- Internationalization support via translation files
- Custom icon for integration and HACS

### Improved
- Device registration for better entity grouping
- Error handling and UI feedback
- Storage and display of historical sensor data
- Documentation in README

### Fixed
- Entity-to-device assignment issues
- Stability when miners are temporarily unreachable
- URL construction for API access

## [1.0.0] - Initial Release

### Added
- Initial release of AxeOS-HA-Integration
- Basic sensor support for BitAxe miners
- Restart button entity
- Configuration flow
- HACS support
