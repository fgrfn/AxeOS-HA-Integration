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

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NAME): str,
        vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): int,
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
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """First step: ask for host, optional name, and scan interval."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            name = user_input.get(CONF_NAME, host).strip()
            scan_interval = user_input.get("scan_interval", DEFAULT_SCAN_INTERVAL)

            if not host:
                errors["host"] = "invalid_host"
            else:
                session = async_get_clientsession(self.hass)
                api = AxeOSAPI(session, host)
                try:
                    info = await api.get_system_info()
                    if info is None:
                        raise CannotConnect
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except Exception:
                    errors["base"] = "unknown"
                else:
                    # Abort if host already configured
                    self._async_abort_entries_match({CONF_HOST: host})
                    return self.async_create_entry(
                        title=name or host,
                        data={
                            CONF_HOST: host,
                            CONF_NAME: name,
                            "scan_interval": scan_interval,
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class AxeOSOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle option flow, e.g. scan_interval, logging."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        options = self.config_entry.options or {}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    "scan_interval",
                    default=options.get("scan_interval", DEFAULT_SCAN_INTERVAL),
                ): int,
                vol.Optional(
                    "logging_level",
                    default=options.get("logging_level", "info"),
                ): vol.In(["debug", "info", "warning", "error"]),
                vol.Optional(
                    "hide_temperature_sensors",
                    default=options.get("hide_temperature_sensors", False),
                ): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
