<div align="center">

<img src="https://raw.githubusercontent.com/fgrfn/AxeOS-HA-Integration/main/brand/logo.png" alt="AxeOS HA Integration logo" width="200">

# AxeOS Home Assistant Integration

**Monitor and control your BitAxe & NerdAxe Bitcoin miners — right from Home Assistant.**

[![GitHub Release](https://img.shields.io/github/v/release/fgrfn/AxeOS-HA-Integration?style=for-the-badge)](https://github.com/fgrfn/AxeOS-HA-Integration/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-success?style=for-the-badge)](https://github.com/fgrfn/AxeOS-HA-Integration)

</div>

---

## 🌟 Highlights

| | |
|---|---|
| 📊 **80+ sensors** | Power, hashrate (instant / 1m / 10m / 1h / 1d), temperatures, shares, difficulty, network, hardware diagnostics |
| 🎛️ **Full control** | Fan speed, frequency and core voltage as number entities, restart button, custom services for automations |
| 🔌 **Device support** | BitAxe (standard AxeOS firmware) and NerdAxe (extended API) with automatic capability detection |
| 🧩 **HA native** | Device classes, state classes, entity categories, long-term statistics, availability tracking |
| 🌍 **Multi-miner** | Unlimited miners as separate devices; English and German translations |

---

## 📦 Installation

> **Requirement:** Home Assistant 2024.11 or newer.

### HACS (Recommended)

[![Open your Home Assistant instance and add this repository to HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=fgrfn&repository=AxeOS-HA-Integration&category=integration)

1. Open **HACS** in your Home Assistant instance
2. Click the **3-dot menu** (top right) → **Custom repositories**
3. Add repository:
   - **URL:** `https://github.com/fgrfn/AxeOS-HA-Integration`
   - **Category:** Integration
4. Search for **"AxeOS HA Integration"**, click **Download**, and restart Home Assistant

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

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=axeos_ha_integration)

1. Go to **Settings** → **Devices & Services** → **+ Add Integration**
2. Search for **"AxeOS HA Integration"**
3. Enter:
   - **Host:** IP address or hostname of your miner (e.g. `192.168.1.100`)
   - **Name:** Optional friendly name (e.g. "BitAxe Gamma")
   - **Scan Interval:** How often to poll data (default: 30 seconds)

### Options

After setup, click **Configure** on the integration to adjust:

| Option | Description | Default |
|--------|-------------|---------|
| **Scan Interval** | Update frequency in seconds | 30 |
| **Logging Level** | Debug, Info, Warning, Error | Info |
| **Hide Temperature Sensors** | Hide temp/vrTemp/temptarget | Disabled |

---

## 📊 Entities

<details>
<summary><b>Sensors (80+)</b> — click to expand</summary>

#### Power & Performance
- Power Consumption (W), Voltage (mV), Current (mA)
- Core Voltage Target & Actual (mV)
- Min/Max Power & Voltage limits
- Frequency (MHz)

#### Hashrate
- Current Hashrate (GH/s) with min/max/avg history attributes
- 1 minute / 10 minutes / 1 hour / 1 day averages
- Expected Hashrate

#### Temperature
- Chip Temperature (°C), VR Temperature (°C)
- Temperature Target & Overheat Temperature (°C)
- PID Controller values (P, I, D)

#### Mining Statistics
- Shares Accepted / Rejected (incl. rejection reasons)
- Best Difficulty (session & total), Pool Difficulty
- Found Blocks (session & total), Duplicate HW Nonces

#### Network
- IP Address, Hostname, MAC Address
- WiFi SSID, Status & Signal Strength (dBm)

#### Hardware
- ASIC Count & Model, Core Count
- Fan Speed (%) & RPM, Manual Fan Speed
- Free Heap Memory, Uptime

#### Configuration & Firmware
- Stratum URL / Port / User (incl. fallback)
- Firmware Version, Board/Device Model
- Running Partition, Last Reset Reason

#### NerdAxe Specific
- VR Frequency, Job Interval
- Pool Mode & Balance, Stratum pool details
- Default Theme

</details>

<details>
<summary><b>Binary Sensors (12+)</b> — click to expand</summary>

- Overheat Mode
- Using Fallback Stratum
- Shutdown Status
- Keep Stratum Connection
- OTP Status
- Enonce Subscribe settings

</details>

<details>
<summary><b>Controls</b> — click to expand</summary>

#### Number Entities
- **Fan Speed** — slider (0–100 %)
- **Frequency** — box (200–600 MHz)
- **Core Voltage** — box (1000–1400 mV)

#### Switches
- Auto Fan Speed, Invert Fan Polarity
- Flip Screen, Invert Screen, Auto Screen Off

#### Button
- **Restart** — reboot the miner

#### Services
- `axeos_ha_integration.restart_miner`
- `axeos_ha_integration.set_frequency`
- `axeos_ha_integration.set_voltage`
- `axeos_ha_integration.set_fanspeed`

</details>

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
      - action: button.press
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
      - action: notify.mobile_app
        data:
          title: "⚠️ Miner Alert"
          message: "BitAxe Gamma hashrate dropped to {{ states('sensor.bitaxe_gamma_current_hashrate') }} GH/s"
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
      - action: number.set_value
        target:
          entity_id: number.bitaxe_gamma_fan_speed
        data:
          value: 100
```

### Service Calls

The services take the miner entity as a data field:

```yaml
# Restart miner
action: axeos_ha_integration.restart_miner
data:
  entity_id: sensor.bitaxe_gamma_power_consumption

# Set frequency
action: axeos_ha_integration.set_frequency
data:
  entity_id: sensor.bitaxe_gamma_power_consumption
  frequency: 525

# Set voltage
action: axeos_ha_integration.set_voltage
data:
  entity_id: sensor.bitaxe_gamma_power_consumption
  voltage: 1250
```

---

## 📱 Dashboard Examples

<details>
<summary><b>Entities Card</b></summary>

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

</details>

<details>
<summary><b>Gauge Card</b></summary>

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

</details>

<details>
<summary><b>History Graph Card</b></summary>

```yaml
type: history-graph
entities:
  - entity: sensor.bitaxe_gamma_current_hashrate
  - entity: sensor.bitaxe_gamma_power_consumption
  - entity: sensor.bitaxe_gamma_chip_temperature
hours_to_show: 24
refresh_interval: 0
```

</details>

---

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

**Latest version (1.11.0):**
- 🔧 Compatibility with current Home Assistant releases (options flow fix, coordinator config entry)
- 🔧 Requires Home Assistant 2024.11 or newer
- 🔧 Fixed hashrate history losing its first sample
- 🔧 Fixed service definitions (removed incompatible target selector)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

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
