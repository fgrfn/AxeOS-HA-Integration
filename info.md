# AxeOS-HA-Integration

A Home Assistant custom integration for monitoring and controlling BitAxe miners running AxeOS.

## Features

- **Real-time System Metrics:** Power, voltage, temperature, hashrate, uptime, and more
- **Miner Restart:** Instantly reboot your miner from Home Assistant
- **Connection Status:** Shows if the miner is online or offline
- **Historical Statistics:** Min/max/average hashrate tracking
- **Device Registration:** Each miner registered as a device with all entities grouped
- **Flexible Configuration:** Scan interval, logging level, hide temperature sensors
- **Multi-Miner Support:** Add as many miners as you want

## Installation

1. Install via HACS (Home Assistant Community Store)
2. Add this repository as a custom repository in HACS
3. Search for "AxeOS-HA-Integration" and install
4. Restart Home Assistant
5. Go to Settings → Integrations → Add Integration → AxeOS-HA-Integration
6. Enter your miner's IP address or hostname

## Configuration Options

After setup, you can configure:
- **Scan Interval:** How often to poll the miner (in seconds)
- **Logging Level:** Debug, info, warning, or error
- **Hide Temperature Sensors:** Option to hide chip/VRM temperature sensors

## Need Help?

Visit the [GitHub repository](https://github.com/fgrfn/AxeOS-HA-Integration) for documentation and support.
