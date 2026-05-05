from __future__ import annotations

from homeassistant.components.number import NumberEntity
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
            if ent.get("type") == "number":
                entities.append(RegSensNumber(api, dev, ent))
    async_add_entities(entities)


class RegSensNumber(NumberEntity):
    def __init__(self, api, device: dict, entity: dict) -> None:
        self.api = api
        self.device = device
        self.entity = entity
        self._value = entity.get("state")
        self._attr_name = f"{device.get('name')} {entity.get('name')}"
        self._attr_unique_id = f"regsens_{device.get('id')}_{entity.get('id')}"
        self._attr_native_min_value = entity.get("min", 0)
        self._attr_native_max_value = entity.get("max", 100)
        self._attr_native_step = entity.get("step", 1)
        self._attr_mode = "slider"

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

    async def async_set_native_value(self, value: float) -> None:
        await self.api.async_set_entity(self.device.get("id"), self.entity.get("id"), value)
        self._value = value
        self.async_write_ha_state()
