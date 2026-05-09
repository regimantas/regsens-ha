from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .discovery import async_setup_regsens_entities
from .entity import RegSensEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    async_setup_regsens_entities(
        entry,
        async_add_entities,
        coordinator,
        "binary_sensor",
        lambda dev, ent: RegSensBinarySensor(coordinator, dev, ent),
    )


class RegSensBinarySensor(RegSensEntity, BinarySensorEntity):
    def __init__(self, coordinator, device: dict, entity: dict) -> None:
        super().__init__(coordinator, device, entity)
        if self.regsens_entity_id == "online":
            self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self):
        entity = self.current_entity
        return bool(entity.get("state")) if entity else None
