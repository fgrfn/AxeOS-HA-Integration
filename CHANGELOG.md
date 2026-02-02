# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
