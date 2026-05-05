from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import RegSensEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    coordinator = data["coordinator"]

    entities = []
    for dev in coordinator.data or []:
        for ent in dev.get("entities", []):
            if ent.get("type") == "number":
                entities.append(RegSensNumber(api, coordinator, dev, ent))
    async_add_entities(entities)


class RegSensNumber(RegSensEntity, NumberEntity):
    def __init__(self, api, coordinator, device: dict, entity: dict) -> None:
        super().__init__(coordinator, device, entity)
        self.api = api
        self._attr_native_min_value = entity.get("min", 0)
        self._attr_native_max_value = entity.get("max", 100)
        self._attr_native_step = entity.get("step", 1)
        self._attr_mode = "slider"

    @property
    def native_value(self):
        entity = self.current_entity
        return entity.get("state") if entity else None

    async def async_set_native_value(self, value: float) -> None:
        await self.api.async_set_entity(self.device_id, self.entity_id, value)
        await self.coordinator.async_request_refresh()
