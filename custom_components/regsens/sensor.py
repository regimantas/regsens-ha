from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import RegSensEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = []
    for dev in coordinator.data or []:
        for ent in dev.get("entities", []):
            if ent.get("type") == "sensor":
                entities.append(RegSensSensor(coordinator, dev, ent))
    async_add_entities(entities)


class RegSensSensor(RegSensEntity, SensorEntity):
    def __init__(self, coordinator, device: dict, entity: dict) -> None:
        super().__init__(coordinator, device, entity)
        self._attr_native_unit_of_measurement = entity.get("unit")

    @property
    def native_value(self):
        entity = self.current_entity
        return entity.get("state") if entity else None
