# AxeOS Home Assistant Integration

[![GitHub Release](https://img.shields.io/github/v/release/fgrfn/AxeOS-HA-Integration?style=for-the-badge)](https://github.com/fgrfn/AxeOS-HA-Integration/releases)
[![License](https://img.shields.io/github/license/fgrfn/AxeOS-HA-Integration?style=for-the-badge)](LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-success?style=for-the-badge)](https://github.com/fgrfn/AxeOS-HA-Integration)

A comprehensive Home Assistant custom integration for monitoring and controlling **BitAxe** and **NerdAxe** Bitcoin miners.

<p align="center">
  <img src="logo@2x.png" alt="AxeOS HA Integration" width="200">
</p>

---

## 🌟 Features

### 📊 **Comprehensive Monitoring**
- **80+ Sensors** covering all aspects of your miner
- Real-time power consumption, voltage, current, and temperature
- Multiple hashrate metrics (instant, 1m, 10m, 1h, 1d averages)
- Mining statistics (shares, difficulty, blocks found)
- Network information (IP, WiFi, signal strength)
- Hardware diagnostics (heap memory, uptime, reset reasons)

### 🎛️ **Full Control**
- **Number Entities** for adjusting settings on the fly:
  - Fan speed (0-100%)
  - Frequency (200-600 MHz)
  - Core voltage (1000-1400 mV)
- **Custom Services** for automation:
  - `restart_miner` - Reboot your miner
  - `set_frequency` - Change mining frequency
  - `set_voltage` - Adjust core voltage
- **Button Entity** for quick restart

### 🔧 **Advanced Features**
- **Binary Sensors** for boolean states (overheat mode, fallback stratum, fan settings)
- **Entity Categories** for organized UI (diagnostic, config)
- **Device Classes** for proper sensor types (power, voltage, temperature, etc.)
- **State Classes** for long-term statistics (measurement, total increasing)
- **Display Precision** for clean value presentation
- **Availability Tracking** - Entities show as unavailable when miner is offline

### 🚀 **Device Support**
- ✅ **BitAxe** - All models with standard AxeOS firmware
- ✅ **NerdAxe** - ESP-Miner-NerdAxe devices with extended API
- Automatic detection of device capabilities
- Support for both flat and nested API structures

### 🌐 **Multi-Miner & Internationalization**
- Add unlimited miners as separate integration instances
- Each miner registered as its own device
- Translations available (English, German)
- HACS compatible for easy installation and updates

---

## 📦 Installation

### HACS (Recommended)

1. Open **HACS** in your Home Assistant instance
2. Navigate to **Integrations**
3. Click the **3-dot menu** (top right) → **Custom repositories**
4. Add repository:
   - **URL:** `https://github.com/fgrfn/AxeOS-HA-Integration`
   - **Category:** Integration
5. Click **Explore & Download Repositories**
6. Search for **"AxeOS HA Integration"**
7. Click **Download** and restart Home Assistant

### Manual Installation

1. Download the [latest release](https://github.com/fgrfn/AxeOS-HA-Integration/releases)
2. Extract and copy the `axeos_ha_integration` folder to:
   ```
   /config/custom_components/axeos_ha_integration/
   ```
3. Restart Home Assistant

---

## ⚙️ Configuration

### Adding a Miner

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **"AxeOS HA Integration"**
4. Enter:
   - **Host:** IP address or hostname of your miner (e.g., `192.168.1.100`)
   - **Name:** Optional friendly name (e.g., "BitAxe Gamma")
   - **Scan Interval:** How often to poll data (default: 30 seconds)
5. Click **Submit**

### Configuration Options

After setup, click **Configure** on the integration to adjust:

| Option | Description | Default |
|--------|-------------|---------|
| **Scan Interval** | Update frequency in seconds | 30 |
| **Logging Level** | Debug, Info, Warning, Error | Info |
| **Hide Temperature Sensors** | Hide temp/vrTemp/temptarget | Disabled |

---

## 📊 Entities Overview

### Sensors (80+)

#### Power & Performance
- Power Consumption (W)
- Voltage (mV), Current (mA)
- Core Voltage Target & Actual (mV)
- Min/Max Power & Voltage limits
- Frequency (MHz)

#### Hashrate Metrics
- Current Hashrate (H/s)
- Hashrate 1 minute average
- Hashrate 10 minutes average
- Hashrate 1 hour average
- Hashrate 1 day average
- Expected Hashrate

#### Temperature
- Chip Temperature (°C)
- VR Temperature (°C)
- Temperature Target (°C)
- Overheat Temperature (°C)
- PID Controller values (P, I, D)

#### Mining Statistics
- Shares Accepted
- Shares Rejected
- Best Difficulty (session & total)
- Pool Difficulty
- Found Blocks (session & total)
- Duplicate HW Nonces

#### Network
- IP Address
- WiFi SSID & Status
- WiFi Signal Strength (dBm)
- MAC Address
- Hostname

#### Hardware
- ASIC Count & Model
- Core Count
- Fan Speed (%) & RPM
- Manual Fan Speed
- Free Heap Memory
- Uptime (seconds)

#### Configuration
- Stratum URL, Port, User
- Fallback Stratum settings
- Firmware Version
- Board/Device Model
- Running Partition
- Last Reset Reason

#### NerdAxe Specific
- VR Frequency
- Job Interval
- Pool Mode & Balance
- Stratum pool details
- Default Theme

### Binary Sensors (12+)
- Overheat Mode
- Using Fallback Stratum
- Auto Fan Speed
- Invert Fan Polarity
- Flip/Invert Screen
- Shutdown Status
- Auto Screen Off
- Keep Stratum Connection
- OTP Status
- Enonce Subscribe settings

### Number Entities (3)
Editable settings with proper validation:
- **Fan Speed** - Slider (0-100%)
- **Frequency** - Box (200-600 MHz)
- **Core Voltage** - Box (1000-1400 mV)

### Button
- **Restart** - Reboot the miner

---

## 🤖 Automation Examples

### Restart on High Temperature

```yaml
automation:
  - alias: "Restart Miner on Overheat"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bitaxe_gamma_chip_temperature
        above: 75
    action:
      - service: button.press
        target:
          entity_id: button.bitaxe_gamma_restart
```

### Notify on Low Hashrate

```yaml
automation:
  - alias: "Alert on Low Hashrate"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bitaxe_gamma_current_hashrate
        below: 400
        for:
          minutes: 5
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Miner Alert"
          message: "BitAxe Gamma hashrate dropped to {{ states('sensor.bitaxe_gamma_current_hashrate') }} H/s"
```

### Adjust Fan Based on Temperature

```yaml
automation:
  - alias: "Dynamic Fan Control"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bitaxe_gamma_chip_temperature
        above: 60
    action:
      - service: number.set_value
        target:
          entity_id: number.bitaxe_gamma_fan_speed
        data:
          value: 100
```

### Service Call Examples

```yaml
# Restart miner
service: axeos_ha_integration.restart_miner
target:
  entity_id: sensor.bitaxe_gamma_power_consumption

# Set frequency
service: axeos_ha_integration.set_frequency
target:
  entity_id: sensor.bitaxe_gamma_power_consumption
data:
  frequency: 525

# Set voltage
service: axeos_ha_integration.set_voltage
target:
  entity_id: sensor.bitaxe_gamma_power_consumption
data:
  voltage: 1250
```

---

## 📱 Lovelace Dashboard Examples

### Entities Card

```yaml
type: entities
title: BitAxe Gamma
entities:
  - entity: sensor.bitaxe_gamma_power_consumption
    name: Power
  - entity: sensor.bitaxe_gamma_current_hashrate
    name: Hashrate
  - entity: sensor.bitaxe_gamma_chip_temperature
    name: Temperature
  - entity: sensor.bitaxe_gamma_accepted_shares
    name: Shares
  - entity: number.bitaxe_gamma_fan_speed
    name: Fan Speed
  - entity: button.bitaxe_gamma_restart
    name: Restart
```

### Gauge Card

```yaml
type: gauge
entity: sensor.bitaxe_gamma_chip_temperature
name: Temperature
min: 0
max: 100
severity:
  green: 0
  yellow: 65
  red: 75
```

### History Graph Card

```yaml
type: history-graph
entities:
  - entity: sensor.bitaxe_gamma_current_hashrate
  - entity: sensor.bitaxe_gamma_power_consumption
  - entity: sensor.bitaxe_gamma_chip_temperature
hours_to_show: 24
refresh_interval: 0
```

---

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

### Latest Version (1.0.8)
- ✨ Full NerdAxe device support with 25+ additional sensors
- ✨ Extended hashrate metrics (1m, 10m, 1h, 1d)
- ✨ PID controller monitoring
- ✨ Stratum pool details
- ✨ Hardware diagnostics
- 🔧 Improved nested data path support

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

```
Copyright (c) 2025 fgrfn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🔗 Links

- **GitHub Repository:** [fgrfn/AxeOS-HA-Integration](https://github.com/fgrfn/AxeOS-HA-Integration)
- **Issue Tracker:** [Report Issues](https://github.com/fgrfn/AxeOS-HA-Integration/issues)
- **BitAxe Project:** [BitMaker-hub/ESP-Miner](https://github.com/BitMaker-hub/ESP-Miner)
- **NerdAxe Firmware:** [BitMaker-hub/ESP-Miner-NerdAxe](https://github.com/BitMaker-hub/ESP-Miner-NerdAxe)
- **Home Assistant:** [home-assistant.io](https://www.home-assistant.io/)
- **HACS:** [hacs.xyz](https://hacs.xyz/)

---

<p align="center">
  <b>Made with ❤️ for the Bitcoin mining community</b>
</p>
