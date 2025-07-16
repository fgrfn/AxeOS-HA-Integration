"""Config Flow for AxeOS-HA-Integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant import exceptions

from .const import DOMAIN, CONF_HOST, CONF_NAME, DEFAULT_SCAN_INTERVAL
from .api import AxeOSAPI


# Schema: We ask for two fields – Host (IP address) and optionally a name
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NAME): str,
    }
)


class CannotConnect(exceptions.HomeAssistantError):
    """Error: Cannot connect to AxeOS miner."""


class AxeOSHaIntegrationConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):
    """Handle a config flow for AxeOS-HA-Integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """First step: Ask for host (IP) and optional name."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            name = user_input.get(CONF_NAME, host).strip()

            # Validation: Host must not be empty
            if not host:
                errors["host"] = "invalid_host"
            else:
                session = async_get_clientsession(self.hass)
                api = AxeOSAPI(session, host)
                try:
                    system_info = await api.get_system_info()
                    if system_info is None:
                        raise CannotConnect
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except Exception:
                    errors["base"] = "unknown"
                else:
                    self._async_abort_entries_match({CONF_HOST: host})
                    return self.async_create_entry(
                        title=name,
                        data={CONF_HOST: host, CONF_NAME: name},
                    )

        data_schema = vol.Schema({
            vol.Required("host"): str,
            vol.Required("name"): str,
            vol.Optional("scan_interval", default=30): int,  # <--- Scan-Intervall hinzufügen
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )


class AxeOSOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("scan_interval", default=self.config_entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)): int,
                vol.Optional("logging_level", default="info"): vol.In(["debug", "info", "warning", "error"]),
                vol.Optional("hide_temp_sensor", default=False): bool,
            }),
        )
