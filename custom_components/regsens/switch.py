from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .discovery import async_setup_regsens_entities
from .entity import RegSensEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    coordinator = data["coordinator"]

    async_setup_regsens_entities(
        entry,
        async_add_entities,
        coordinator,
        "switch",
        lambda dev, ent: RegSensSwitch(api, coordinator, dev, ent),
    )


class RegSensSwitch(RegSensEntity, SwitchEntity):
    def __init__(self, api, coordinator, device: dict, entity: dict) -> None:
        super().__init__(coordinator, device, entity)
        self.api = api

    @property
    def is_on(self):
        entity = self.current_entity
        return bool(entity.get("state")) if entity else None

    async def async_turn_on(self, **kwargs):
        response = await self.api.async_set_entity(self.regsens_device_id, self.regsens_entity_id, True)
        self.coordinator.async_apply_entity_state(
            self.regsens_device_id,
            self.regsens_entity_id,
            response.get("value", True),
        )

    async def async_turn_off(self, **kwargs):
        response = await self.api.async_set_entity(self.regsens_device_id, self.regsens_entity_id, False)
        self.coordinator.async_apply_entity_state(
            self.regsens_device_id,
            self.regsens_entity_id,
            response.get("value", False),
        )
