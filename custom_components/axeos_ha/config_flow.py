"""Config Flow für BitAxe Integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant import exceptions

from .const import DOMAIN, CONF_HOST, CONF_NAME
from .api import AxeOSAPI

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NAME): str,
    }
)

class CannotConnect(exceptions.HomeAssistantError):
    """Fehler: Kann zum AxeOS Miner keine Verbindung aufbauen."""

class AxeOSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BitAxe."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> FlowResult:
        """Erster Schritt: Abfrage von Host (IP) + optional Name."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            name = user_input.get(CONF_NAME, host).strip()

            # Einfache Validierung: Ist Host nicht leer?
            if not host:
                errors["host"] = "invalid_host"
            else:
                # Prüfe Verbindung, indem wir einen Client-Request an /api/system/info senden
                session = async_get_clientsession(self.hass)
                api = AxeOSAPI(session, host)
                try:
                    system_info = await api.get_system_info()
                    if system_info is None:
                        raise CannotConnect
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except Exception:
                    errors["base"] = "cannot_connect"
                else:
                    # Doppelte Einträge vermeiden
                    await self._async_abort_entries_match({CONF_HOST: host})
                    return self.async_create_entry(
                        title=name,
                        data={CONF_HOST: host, CONF_NAME: name},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
