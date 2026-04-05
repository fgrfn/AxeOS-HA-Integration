import asyncio
import aiohttp
import logging

from .const import (
    API_SYSTEM,
    API_SYSTEM_INFO,
    API_SYSTEM_RESTART,
    API_SYSTEM_FREQUENCY,
    API_SYSTEM_VOLTAGE,
    API_SYSTEM_FANSPEED,
)

_LOGGER = logging.getLogger(__name__)

class AxeOSAPI:
    """Client class to communicate with an AxeOS miner via HTTP.
       Only the /api/system/info endpoint is queried."""

    def __init__(self, session: aiohttp.ClientSession, host: str):
        # Remove protocol if already present
        if host.startswith("http://"):
            host = host[len("http://"):]
        self.session = session
        self.host = host
        self.system_info = {}

    async def get_system_info(self) -> dict | None:
        """Fetches system info (GET /api/system/info)."""
        url = f"http://{self.host}{API_SYSTEM_INFO}"
        try:
            async with asyncio.timeout(10):
                resp = await self.session.get(url)
                if resp.status == 200:
                    self.system_info = await resp.json()
                    return self.system_info
                _LOGGER.error("Error fetching system info from %s: %s", url, resp.status)
                return None
        except Exception as e:
            _LOGGER.error("Exception fetching system info from %s: %s", self.host, e)
            return None

    async def restart_system(self) -> bool:
        """Restarts the miner (POST /api/system/restart)."""
        url = f"http://{self.host}{API_SYSTEM_RESTART}"
        try:
            async with asyncio.timeout(10):
                resp = await self.session.post(url)
                if resp.status == 200:
                    _LOGGER.info("Restart command sent successfully to %s", self.host)
                    return True
                _LOGGER.error("Error restarting miner at %s: %s", url, resp.status)
                return False
        except Exception as e:
            _LOGGER.error("Exception when restarting miner at %s: %s", self.host, e)
            return False

    async def set_frequency(self, frequency: int) -> bool:
        """Set the mining frequency."""
        url = f"http://{self.host}{API_SYSTEM_FREQUENCY}"
        try:
            async with asyncio.timeout(10):
                resp = await self.session.post(url, json={"frequency": frequency})
                if resp.status == 200:
                    _LOGGER.info("Frequency set to %s MHz on %s", frequency, self.host)
                    return True
                _LOGGER.error("Error setting frequency on %s: %s", url, resp.status)
                return False
        except Exception as e:
            _LOGGER.error("Exception setting frequency on %s: %s", self.host, e)
            return False

    async def set_voltage(self, voltage: int) -> bool:
        """Set the core voltage."""
        url = f"http://{self.host}{API_SYSTEM_VOLTAGE}"
        try:
            async with asyncio.timeout(10):
                resp = await self.session.post(url, json={"voltage": voltage})
                if resp.status == 200:
                    _LOGGER.info("Voltage set to %s mV on %s", voltage, self.host)
                    return True
                _LOGGER.error("Error setting voltage on %s: %s", url, resp.status)
                return False
        except Exception as e:
            _LOGGER.error("Exception setting voltage on %s: %s", self.host, e)
            return False

    async def set_fanspeed(self, fanspeed: int) -> bool:
        """Set the fan speed percentage."""
        url = f"http://{self.host}{API_SYSTEM_FANSPEED}"
        try:
            async with asyncio.timeout(10):
                resp = await self.session.post(url, json={"fanspeed": fanspeed})
                if resp.status == 200:
                    _LOGGER.info("Fan speed set to %s%% on %s", fanspeed, self.host)
                    return True
                _LOGGER.error("Error setting fan speed on %s: %s", url, resp.status)
                return False
        except Exception as e:
            _LOGGER.error("Exception setting fan speed on %s: %s", self.host, e)
            return False

    async def set_setting(self, key: str, value: bool) -> bool:
        """Update a boolean setting via PATCH /api/system."""
        url = f"http://{self.host}{API_SYSTEM}"
        try:
            async with asyncio.timeout(10):
                resp = await self.session.patch(url, json={key: value})
                if resp.status == 200:
                    _LOGGER.info("Setting %s=%s on %s", key, value, self.host)
                    return True
                _LOGGER.error("Error setting %s on %s: %s", key, self.host, resp.status)
                return False
        except Exception as e:
            _LOGGER.error("Exception setting %s on %s: %s", key, self.host, e)
            return False
