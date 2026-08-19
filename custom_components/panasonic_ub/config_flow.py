"""Config flow for Panasonic UB Blu-ray integration."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_MAC, CONF_NAME
from homeassistant.core import callback

from .const import (
    CONF_AUTH_ENABLE,
    CONF_KEY,
    CONF_POLL_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
)


class PanasonicUBConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Panasonic UB."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return PanasonicUBOptionsFlowHandler()

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_NAME, DEFAULT_NAME), data=user_input
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_MAC): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional(CONF_KEY): str,  # No default value
                vol.Optional(CONF_AUTH_ENABLE, default=True): bool,
                vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"device_name": "Panasonic Player"},
        )


class PanasonicUBOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the integration."""

    # FIX: __init__ removed.
    # self.config_entry is automatically populated by Home Assistant before async_step_init is called.

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # When options are saved, we update the main config entry data
            # so the changes persist and require a reload.
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=user_input,  # Overwrite main data with new input
            )
            return self.async_create_entry(title="", data={})

        # Load current values from the config entry
        current_data = self.config_entry.data

        # Build schema with current values as defaults
        options_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current_data.get(CONF_HOST)): str,
                vol.Optional(CONF_MAC, default=current_data.get(CONF_MAC)): str,
                vol.Optional(
                    CONF_NAME, default=current_data.get(CONF_NAME, DEFAULT_NAME)
                ): str,
                vol.Optional(CONF_KEY, default=current_data.get(CONF_KEY, "")): str,
                vol.Optional(
                    CONF_AUTH_ENABLE, default=current_data.get(CONF_AUTH_ENABLE, True)
                ): bool,
                vol.Optional(
                    CONF_POLL_INTERVAL,
                    default=current_data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
                ): int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
