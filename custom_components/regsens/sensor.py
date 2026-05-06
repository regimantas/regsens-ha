from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
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
        "sensor",
        lambda dev, ent: RegSensSensor(coordinator, dev, ent),
    )


class RegSensSensor(RegSensEntity, SensorEntity):
    def __init__(self, coordinator, device: dict, entity: dict) -> None:
        super().__init__(coordinator, device, entity)
        unit = entity.get("unit")
        self._attr_native_unit_of_measurement = self._normalize_unit(unit)

        if self._is_temperature_sensor(entity):
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_suggested_display_precision = 1

    @property
    def native_value(self):
        entity = self.current_entity
        return entity.get("state") if entity else None

    @staticmethod
    def _normalize_unit(unit):
        if str(unit).strip().lower() in {"c", "°c", "celsius"}:
            return UnitOfTemperature.CELSIUS
        return unit

    def _is_temperature_sensor(self, entity: dict) -> bool:
        entity_id = str(entity.get("id") or "").lower()
        name = str(entity.get("name") or "").lower()
        unit = str(entity.get("unit") or "").strip().lower()
        return (
            entity_id in {"temperature", "temp"}
            or "temperature" in name
            or unit in {"c", "°c", "celsius"}
        )
