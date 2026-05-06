from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_API_URL, DOMAIN, CONF_API_KEY
from .api import RegSensApi, RegSensApiError


class RegSensConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            session = async_get_clientsession(self.hass)
            api = RegSensApi(DEFAULT_API_URL, api_key, session)

            try:
                await api.async_get_devices()
            except RegSensApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(DEFAULT_API_URL)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="RegSens",
                    data={CONF_API_KEY: api_key},
                )

        schema = vol.Schema({
            vol.Required(CONF_API_KEY): vol.All(str, vol.Length(min=1)),
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
