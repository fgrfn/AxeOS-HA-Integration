import async_timeout
import aiohttp
import logging

from .const import API_SYSTEM_INFO

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
