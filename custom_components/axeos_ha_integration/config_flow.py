"""Config Flow für AxeOS-HA-Integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant import exceptions

from .const import DOMAIN, CONF_HOST, CONF_NAME
from .api import AxeOSAPI


# Schema: Wir fragen zwei Felder ab – Host (IP-Adresse) und optional einen Namen
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NAME): str,
    }
)


class CannotConnect(exceptions.HomeAssistantError):
    """Fehler: Kann zum AxeOS Miner keine Verbindung aufbauen."""


class AxeOSHaIntegrationConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):
    """Handle a config flow for AxeOS-HA-Integration."""

    VERSION = 1  # Versionsnummer des Flows (muss vorhanden sein)

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Erster Schritt: Host (IP) und optionaler Name abfragen."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            name = user_input.get(CONF_NAME, host).strip()

            # Validierung: Host darf nicht leer sein
            if not host:
                errors["host"] = "invalid_host"
            else:
                # Versuche, eine Verbindung zum Miner herzustellen
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
                    # Verhindere doppelte Einträge mit demselben Host
                    self._async_abort_entries_match({CONF_HOST: host})
                    return self.async_create_entry(
                        title=name,
                        data={CONF_HOST: host, CONF_NAME: name},
                    )

        # Wenn wir hier landen, ist user_input None oder es gab Validierungsfehler
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
