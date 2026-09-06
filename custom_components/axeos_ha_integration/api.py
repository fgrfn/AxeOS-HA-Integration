import asyncio
import logging
from typing import Any, cast

import aiohttp

from .const import (
    API_SYSTEM,
    API_SYSTEM_FANSPEED,
    API_SYSTEM_FREQUENCY,
    API_SYSTEM_INFO,
    API_SYSTEM_RESTART,
    API_SYSTEM_VOLTAGE,
)

_LOGGER = logging.getLogger(__name__)

API_TIMEOUT = 10


class AxeOSApiError(Exception):
    """Raised when communication with an AxeOS miner fails."""


class AxeOSAPI:
    """Client class to communicate with an AxeOS miner via HTTP.
    Only the /api/system/info endpoint is queried."""

    def __init__(self, session: aiohttp.ClientSession, host: str):
        # Remove protocol if already present
        if host.startswith("http://"):
            host = host[len("http://") :]
        self.session = session
        self.host = host
        self.system_info = {}

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        expect_json: bool = False,
    ) -> dict[str, Any] | bool:
        """Send a request and ensure the response is always released."""
        url = f"http://{self.host}{path}"
        try:
            async with asyncio.timeout(API_TIMEOUT):
                async with self.session.request(
                    method, url, json=json_body
                ) as response:
                    if response.status != 200:
                        raise AxeOSApiError(
                            f"AxeOS request to {url} returned HTTP {response.status}"
                        )

                    if not expect_json:
                        return True

                    payload = await response.json()
                    if not isinstance(payload, dict):
                        raise AxeOSApiError(
                            f"AxeOS request to {url} returned an invalid response"
                        )
                    return cast(dict[str, Any], payload)
        except TimeoutError as err:
            raise AxeOSApiError(f"AxeOS request to {url} timed out") from err
        except aiohttp.ClientError as err:
            raise AxeOSApiError(f"AxeOS request to {url} failed: {err}") from err
        except ValueError as err:
            raise AxeOSApiError(
                f"AxeOS request to {url} returned invalid JSON"
            ) from err

    async def get_system_info(self) -> dict[str, Any]:
        """Fetches system info (GET /api/system/info)."""
        self.system_info = cast(
            dict[str, Any],
            await self._request("GET", API_SYSTEM_INFO, expect_json=True),
        )
        return self.system_info

    async def restart_system(self) -> bool:
        """Restarts the miner (POST /api/system/restart)."""
        await self._request("POST", API_SYSTEM_RESTART)
        _LOGGER.info("Restart command sent successfully to %s", self.host)
        return True

    async def set_frequency(self, frequency: int) -> bool:
        """Set the mining frequency."""
        await self._request(
            "POST", API_SYSTEM_FREQUENCY, json_body={"frequency": frequency}
        )
        _LOGGER.info("Frequency set to %s MHz on %s", frequency, self.host)
        return True

    async def set_voltage(self, voltage: int) -> bool:
        """Set the core voltage."""
        await self._request("POST", API_SYSTEM_VOLTAGE, json_body={"voltage": voltage})
        _LOGGER.info("Voltage set to %s mV on %s", voltage, self.host)
        return True

    async def set_fanspeed(self, fanspeed: int) -> bool:
        """Set the fan speed percentage."""
        await self._request(
            "POST", API_SYSTEM_FANSPEED, json_body={"fanspeed": fanspeed}
        )
        _LOGGER.info("Fan speed set to %s%% on %s", fanspeed, self.host)
        return True

    async def set_setting(self, key: str, value: bool) -> bool:
        """Update a boolean setting via PATCH /api/system."""
        await self._request("PATCH", API_SYSTEM, json_body={key: value})
        _LOGGER.info("Setting %s=%s on %s", key, value, self.host)
        return True
