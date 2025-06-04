"""API-Client für AxeOS (AxeOS Miner)."""

import asyncio
import aiohttp
import async_timeout
import logging

from .const import API_SYSTEM_INFO, API_SWARM_INFO, API_SYSTEM_RESTART

_LOGGER = logging.getLogger(__name__)

class AxeOSAPI:
    """Client-Klasse, um mit einem AxeOS Miner (AxeOS) via HTTP zu kommunizieren."""

    def __init__(self, session: aiohttp.ClientSession, host: str):
        """Initialisiere den Client.

        Args:
          session: aiohttp-Session, die Home Assistant bereitstellt.
          host: IP oder Hostname des Miners (z. B. "192.168.1.42").
        """
        self._session = session
        self._base_url = f"http://{host}"

    async def get_system_info(self) -> dict | None:
        """Holt die System-Info (GET /api/system/info)."""
        url = f"{self._base_url}{API_SYSTEM_INFO}"
        try:
            async with async_timeout.timeout(10):
                resp = await self._session.get(url)
                resp.raise_for_status()
                data = await resp.json()
                return data
        except Exception as ex:
            _LOGGER.error("Fehler beim Abruf von System Info von %s: %s", url, ex)
            return None

    async def get_swarm_info(self) -> dict | None:
        """Holt die Swarm-Info (GET /api/swarm/info)."""
        url = f"{self._base_url}{API_SWARM_INFO}"
        try:
            async with async_timeout.timeout(10):
                resp = await self._session.get(url)
                resp.raise_for_status()
                data = await resp.json()
                return data
        except Exception as ex:
            _LOGGER.error("Fehler beim Abruf von Swarm Info von %s: %s", url, ex)
            return None

    async def restart_system(self) -> bool:
        """Sendet POST /api/system/restart, um den Miner neu zu starten."""
        url = f"{self._base_url}{API_SYSTEM_RESTART}"
        try:
            async with async_timeout.timeout(10):
                resp = await self._session.post(url)
                resp.raise_for_status()
                return True
        except Exception as ex:
            _LOGGER.error("Fehler beim Neustarten via %s: %s", url, ex)
            return False
