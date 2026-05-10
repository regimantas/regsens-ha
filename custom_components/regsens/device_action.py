from __future__ import annotations

import voluptuous as vol

from homeassistant.components.device_automation import DEVICE_ACTION_BASE_SCHEMA
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_ENTITY_ID,
    CONF_PLATFORM,
    CONF_TYPE,
    SERVICE_TOGGLE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN

ACTION_TYPES = {SERVICE_TURN_ON, SERVICE_TURN_OFF, SERVICE_TOGGLE}
ACTION_DOMAINS = {"light", "switch"}

ACTION_SCHEMA = DEVICE_ACTION_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_ENTITY_ID): cv.entity_id,
        vol.Required(CONF_TYPE): vol.In(ACTION_TYPES),
    }
)


async def async_get_actions(hass: HomeAssistant, device_id: str) -> list[dict]:
    registry = er.async_get(hass)
    actions: list[dict] = []

    for entry in er.async_entries_for_device(registry, device_id):
        if entry.platform != DOMAIN or entry.domain not in ACTION_DOMAINS:
            continue

        for action_type in ACTION_TYPES:
            actions.append(
                {
                    CONF_PLATFORM: "device",
                    CONF_DOMAIN: DOMAIN,
                    CONF_DEVICE_ID: device_id,
                    CONF_ENTITY_ID: entry.entity_id,
                    CONF_TYPE: action_type,
                }
            )

    return actions


async def async_call_action_from_config(
    hass: HomeAssistant,
    config: dict,
    variables: dict,
    context: Context | None,
) -> None:
    config = ACTION_SCHEMA(config)
    entity_id = config[CONF_ENTITY_ID]
    service_domain = entity_id.split(".", 1)[0]

    await hass.services.async_call(
        service_domain,
        config[CONF_TYPE],
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
        context=context,
    )
