import async_timeout
import aiohttp
import logging

from .const import API_SYSTEM_INFO, API_SYSTEM_RESTART

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
        url = f"http://{self.host}/api/system/info"  # Ensure only one slash
        async with async_timeout.timeout(10):
            resp = await self.session.get(url)
            if resp.status == 200:
                self.system_info = await resp.json()
                return self.system_info
            _LOGGER.error("Error fetching system info from %s: %s", url, resp.status)
            return None

    async def restart_system(self) -> bool:
        """Restarts the miner (POST /api/system/restart)."""
        url = f"http://{self.host}/api/system/restart"
        try:
            async with async_timeout.timeout(10):
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
        url = f"http://{self.host}/api/system/frequency"
        try:
            async with async_timeout.timeout(10):
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
        url = f"http://{self.host}/api/system/voltage"
        try:
            async with async_timeout.timeout(10):
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
        url = f"http://{self.host}/api/system/fanspeed"
        try:
            async with async_timeout.timeout(10):
                resp = await self.session.post(url, json={"fanspeed": fanspeed})
                if resp.status == 200:
                    _LOGGER.info("Fan speed set to %s%% on %s", fanspeed, self.host)
                    return True
                _LOGGER.error("Error setting fan speed on %s: %s", url, resp.status)
                return False
        except Exception as e:
            _LOGGER.error("Exception setting fan speed on %s: %s", self.host, e)
            return False
