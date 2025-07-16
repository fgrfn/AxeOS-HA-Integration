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
        self._session = session
        self._base_url = f"http://{host}"

    async def get_system_info(self) -> dict | None:
        """Fetches system info (GET /api/system/info)."""
        url = f"{self._base_url}/api/system/info"  # Ensure only one slash
        try:
            async with async_timeout.timeout(10):
                resp = await self._session.get(url)
                resp.raise_for_status()
                return await resp.json()
        except Exception as ex:
            _LOGGER.error("Error fetching system info from %s: %s", url, ex)
            return None
