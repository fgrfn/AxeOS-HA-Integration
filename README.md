# AxeOS-HA-Integration *STILL IN ALPHA*

A Home Assistant custom integration for monitoring and controlling BitAxe miners running AxeOS.

---

## Overview

**AxeOS-HA-Integration** lets you integrate your BitAxe (AxeOS) Bitcoin miners directly into Home Assistant. Once installed, you can:

- **Fetch real-time system metrics** such as power consumption, voltage, temperature, hashrate, uptime, and more.
- **Restart miners** with a single button click inside Home Assistant.
- **Register each miner as a device** in Home Assistant’s Device Registry.
- **Create automations and dashboards** based on live miner data—no need to open a separate web UI.

This integration works over your local network (HTTP) and is designed for simplicity, stability, and extensibility.

---

## Features

- **System Metrics**
  - Power (W)
  - Voltage (mV)
  - Current (mA)
  - Chip temperature (°C)
  - VRM temperature (°C)
  - Maximum power (W)
  - Nominal voltage (V)
  - Current and expected hashrate (H/s)
  - Shares accepted / rejected
  - Uptime (seconds)
  - Wi-Fi signal strength (dBm)
  - Free heap memory (bytes)
  - Fan speed (percentage and RPM)
  - Core frequency (MHz)
  - Core voltage (target / actual in mV)
  - ASIC count and model
  - Firmware version, board version, hostname, MAC address, Wi-Fi status

- **Restart Button**  
  A dedicated button entity to reboot the miner via a POST request.

- **Device Registration**  
  Automatically registers each miner in the Device Registry, grouping all related entities under one device.

- **Config Flow**  
  Easy setup through Home Assistant’s Integrations UI—just enter IP (or hostname) and an optional name.

- **HACS-Compatible**  
  Install, update, and manage the integration directly from Home Assistant Community Store.

---

## Installation

### HACS (Recommended)

1. Add this repository to HACS as a **Custom Repository**:  
   - Go to **HACS → Settings → Custom Repositories**.  
   - Enter the repository URL:  
     ```
     https://github.com/fgrfn/AxeOS-HA-Integration
     ```  
   - Select **Integration** as the category and click **Add**.

2. Once added, go to **HACS → Integrations**, search for **AxeOS-HA-Integration**, and click **Install**.

3. Restart Home Assistant.

4. Navigate to **Settings → Integrations → + Add Integration** and search for **AxeOS-HA-Integration**. Enter your miner’s IP or hostname and an optional name.

### Manual Installation

1. Download or clone the repository:
   ```bash
   git clone https://github.com/fgrfn/ha-axeos-integration.git
   ```

2. Copy the `axeos_ha` folder into your Home Assistant `custom_components` directory:
   ```
   /config/custom_components/axeos_ha/
   ```

3. Restart Home Assistant.

4. Go to **Settings → Integrations → + Add Integration** and search for **AxeOS-HA-Integration**. Enter IP or hostname and an optional name.

---

## Configuration

After installation, configure each miner through the UI:

1. **Settings → Integrations → + Add Integration → AxeOS-HA-Integration**  
2. Enter the **Host** (IP address or hostname) of your AxeOS miner.  
3. (Optional) Enter a **Name** for display; defaults to the host if left blank.  
4. Click **Submit**.  
5. The integration will attempt to fetch `/api/system/info`. If successful, Home Assistant will create sensors and a restart button for that miner.

You can add multiple miners—each will appear under its own entry.

---

## Entity List

When you add a miner, the following entities are created (example for miner named “Gamma”):

- **Sensors**  
  - `sensor.gamma_power` – Power consumption (W)  
  - `sensor.gamma_voltage` – Voltage (mV)  
  - `sensor.gamma_current` – Current (mA)  
  - `sensor.gamma_temp` – Chip temperature (°C)  
  - `sensor.gamma_vrTemp` – VRM temperature (°C)  
  - `sensor.gamma_maxPower` – Maximum power (W)  
  - `sensor.gamma_nominalVoltage` – Nominal voltage (V)  
  - `sensor.gamma_hashRate` – Current hashrate (H/s)  
  - `sensor.gamma_expectedHashrate` – Expected hashrate (H/s)  
  - `sensor.gamma_sharesAccepted` – Shares accepted  
  - `sensor.gamma_sharesRejected` – Shares rejected  
  - `sensor.gamma_uptimeSeconds` – Uptime (seconds)  
  - `sensor.gamma_wifiRSSI` – Wi-Fi signal strength (dBm)  
  - `sensor.gamma_freeHeap` – Free heap memory (bytes)  
  - `sensor.gamma_fanspeed` – Fan speed (%)  
  - `sensor.gamma_fanrpm` – Fan RPM  
  - `sensor.gamma_frequency` – Core frequency (MHz)  
  - `sensor.gamma_coreVoltage` – Core voltage (target, mV)  
  - `sensor.gamma_coreVoltageActual` – Core voltage (actual, mV)  
  - `sensor.gamma_asicCount` – ASIC count  
  - `sensor.gamma_smallCoreCount` – Total core count  
  - `sensor.gamma_ASICModel` – ASIC model  
  - `sensor.gamma_version` – Firmware version  
  - `sensor.gamma_ssid` – Wi-Fi SSID  
  - `sensor.gamma_macAddr` – MAC address  
  - `sensor.gamma_hostname` – Hostname  
  - `sensor.gamma_wifiStatus` – Wi-Fi status  

- **Button**  
  - `button.gamma_restart` – Reboot the miner

---

## Usage Examples

### Automations

#### 1. Restart on Overheat

```yaml
alias: "Restart Miner on Overheat"
trigger:
  - platform: numeric_state
    entity_id: sensor.gamma_temp
    above: 80
action:
  - service: button.press
    target:
      entity_id: button.gamma_restart
```

#### 2. Notify on Low Hashrate

```yaml
alias: "Notify on Low Hashrate"
trigger:
  - platform: numeric_state
    entity_id: sensor.gamma_hashRate
    below: 1500
action:
  - service: persistent_notification.create
    data:
      title: "Hashrate Warning"
      message: "Miner Gamma hashrate dropped below 1500 H/s"
```

### Lovelace Dashboard

```yaml
cards:
  - type: entities
    title: "Miner Gamma Status"
    entities:
      - sensor.gamma_power
      - sensor.gamma_hashRate
      - sensor.gamma_temp
      - sensor.gamma_uptimeSeconds
      - button.gamma_restart
```
---

## License

This project is released under the [MIT License](LICENSE).  
