# Release Notes – AxeOS-HA-Integration

## v1.0.4 – July 16, 2025

### New Features
- **Connection Status Sensor:** Shows if the miner is online or offline.
- **Historical Statistics:** Sensors provide min/max/average hashrate as attributes.
- **Advanced UI Options:** Scan interval, logging level, and hiding temperature sensors can be configured directly in the Home Assistant UI.
- **Diagnostic Attributes:** Last error status and rejected share reasons are shown as sensor attributes.
- **Multi-Miner Support:** Multiple miners can be added and managed independently.
- **Internationalization:** UI texts are translatable via `strings.json` and translation files.
- **Improved Logging:** Logging level can be set via integration options.
- **Custom Icon:** Integration and HACS now display a custom icon.

### Improvements
- Device registration for better overview and entity grouping.
- Optimized error handling and feedback in the UI.
- Improved storage and display of historical sensor data.
- Updated README and documentation.

### Bugfixes
- Fixed entity-to-device assignment issues.
- Improved stability when miners are temporarily unreachable.
- Corrected URL construction for API access.

---

**Note:**  
After updating, please restart Home Assistant to ensure all new features and icons are