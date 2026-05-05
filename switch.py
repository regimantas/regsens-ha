from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    devices = data.get("devices") or await api.async_get_devices()

    entities = []
    for dev in devices:
        for ent in dev.get("entities", []):
            if ent.get("type") == "sensor":
                entities.append(RegSensSensor(dev, ent))
    async_add_entities(entities)


class RegSensSensor(SensorEntity):
    def __init__(self, device: dict, entity: dict) -> None:
        self.device = device
        self.entity = entity
        self._attr_name = f"{device.get('name')} {entity.get('name')}"
        self._attr_unique_id = f"regsens_{device.get('id')}_{entity.get('id')}"
        self._attr_native_unit_of_measurement = entity.get("unit")
        self._value = entity.get("state")

    @property
    def native_value(self):
        return self._value

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device.get("id"))},
            "name": self.device.get("name"),
            "manufacturer": self.device.get("manufacturer", "RegSens"),
            "model": self.device.get("model", "RegSens Device"),
        }
