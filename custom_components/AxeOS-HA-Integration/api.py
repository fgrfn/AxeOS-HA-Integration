import async_timeout
import aiohttp
import logging

from .const import API_SYSTEM_INFO

_LOGGER = logging.getLogger(__name__)

class AxeOSAPI:
    """Client-Klasse, um mit einem AxeOS‐Miner via HTTP zu kommunizieren.
       Nur das Endpunkt /api/system/info wird abgefragt."""

    def __init__(self, session: aiohttp.ClientSession, host: str):
        self._session = session
        self._base_url = f"http://{host}"

    async def get_system_info(self) -> dict | None:
        """Holt die System-Info (GET /api/system/info)."""
        url = f"{self._base_url}{API_SYSTEM_INFO}"
        try:
            async with async_timeout.timeout(10):
                resp = await self._session.get(url)
                resp.raise_for_status()
                return await resp.json()
        except Exception as ex:
            _LOGGER.error("Fehler beim Abruf von System Info von %s: %s", url, ex)
            return None
