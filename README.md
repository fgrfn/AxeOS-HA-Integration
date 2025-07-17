# AxeOS-HA-Integration * ALPHA *

A Home Assistant custom integration for monitoring and controlling BitAxe miners running AxeOS.

---

## Overview

**AxeOS-HA-Integration** allows you to integrate your BitAxe (AxeOS) Bitcoin miners directly into Home Assistant.  
Key features include:

- Real-time system metrics (power, voltage, temperature, hashrate, uptime, etc.)
- Miner restart via button or automation
- Device registration in Home Assistant
- Flexible configuration via the Home Assistant UI
- Advanced diagnostics and statistics
- Multi-miner support

---

## Features

- **System Metrics:**  
  Power, voltage, current, chip temperature, VRM temperature, max power, nominal voltage, hashrate, shares accepted/rejected, uptime, Wi-Fi signal strength, free heap, fan speed, frequency, core voltage, ASIC count/model, firmware version, board version, hostname, MAC address, Wi-Fi status, and more.

- **Restart Button:**  
  Instantly reboot your miner from Home Assistant (button entity and service).

- **Connection Status Sensor:**  
  Shows if the miner is online or offline.

- **Statistics:**  
  Historical min/max/average hashrate available as sensor attributes.

- **Device Registration:**  
  Each miner is registered as a device, grouping all related entities.

- **Flexible UI Options:**  
  Configure scan interval, logging level, and hide specific sensors directly from the UI.

- **Advanced Diagnostics:**  
  Last error status and rejected share reasons shown as sensor attributes.

- **Multi-Miner Support:**  
  Add as many miners as you want—each appears as a separate integration.

- **Internationalization:**  
  UI texts are translatable via `strings.json`.

- **HACS-Compatible:**  
  Easy installation and updates via Home Assistant Community Store.

---

## Installation

### HACS (Recommended)

1. Add this repository to HACS as a **Custom Repository**:
   - Go to **HACS → Settings → Custom Repositories**
   - Enter: `https://github.com/fgrfn/AxeOS-HA-Integration`
   - Select **Integration** and click **Add**
2. Go to **HACS → Integrations**, search for **AxeOS-HA-Integration**, and click **Install**
3. Restart Home Assistant

### Manual Installation

1. Download or clone the repository:
   ```bash
   git clone https://github.com/fgrfn/AxeOS-HA-Integration.git
   ```
2. Copy the `axeos_ha_integration` folder into your Home Assistant `custom_components` directory:
   ```
   /config/custom_components/axeos_ha_integration/
   ```
3. Restart Home Assistant

---

## Configuration

Configure each miner via the Home Assistant UI:

1. Go to **Settings → Integrations → + Add Integration → AxeOS-HA-Integration**
2. Enter the **Host** (IP address or hostname) and an optional **Name**
3. Submit the form
4. The integration will fetch `/api/system/info` and create all relevant entities

### Options

After setup, you can adjust:

- **Scan Interval:** How often data is polled (seconds)
- **Logging Level:** Debug, info, warning, error
- **Hide Temperature Sensors:** Optionally hide chip/VRM temperature sensors

---

## Entities

Each miner provides:

- **Sensors:**  
  All system metrics listed above, plus connection status and historical statistics

- **Button:**  
  Restart the miner

---

## Usage Examples

### Automation: Restart on Overheat

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

### Automation: Notify on Low Hashrate

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

### Lovelace Dashboard Example

```yaml
cards:
  - type: entities
    title: "Miner Gamma Status"
    entities:
      - sensor.gamma_power
      - sensor.gamma_hashRate
      - sensor.gamma_temp
      - sensor.gamma_uptimeSeconds
      - sensor.gamma_connection_status
      - button.gamma_restart
```

---

## Troubleshooting

- **Cannot connect:**  
  Check the IP address/hostname and network connectivity.
- **No entities created:**  
  Ensure the miner is running AxeOS and the API is reachable.
- **Errors shown in sensors:**  
  See the `last_error` attribute for details.

---

## License

Released under the [MIT License](LICENSE)
