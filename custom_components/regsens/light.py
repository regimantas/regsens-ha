from __future__ import annotations

from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ATTR_RGB_COLOR, ColorMode, LightEntity
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
        "light",
        lambda dev, ent: RegSensLight(api, coordinator, dev, ent),
    )


class RegSensLight(RegSensEntity, LightEntity):
    def __init__(self, api, coordinator, device: dict[str, Any], entity: dict[str, Any]) -> None:
        super().__init__(coordinator, device, entity)
        self.api = api
        self._attr_supported_color_modes = {ColorMode.RGB}

    @property
    def is_on(self) -> bool | None:
        state = self._light_state
        if state is None:
            return None
        if isinstance(state, dict):
            if "on" in state:
                return bool(state.get("on"))
            return str(state.get("state") or "").upper() == "ON"
        return bool(state)

    @property
    def brightness(self) -> int | None:
        state = self._light_state
        if not isinstance(state, dict):
            return None
        value = state.get("brightness")
        if value is None:
            return None
        return max(0, min(255, int(value)))

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        state = self._light_state
        if not isinstance(state, dict):
            return None
        rgb = state.get("rgb_color")
        if not isinstance(rgb, list | tuple) or len(rgb) < 3:
            return None
        return (
            max(0, min(255, int(rgb[0]))),
            max(0, min(255, int(rgb[1]))),
            max(0, min(255, int(rgb[2]))),
        )

    @property
    def color_mode(self) -> ColorMode:
        return ColorMode.RGB

    @property
    def _light_state(self) -> Any:
        entity = self.current_entity
        return entity.get("state") if entity else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        payload: dict[str, Any] = {"state": "ON"}

        if ATTR_BRIGHTNESS in kwargs:
            payload["brightness"] = kwargs[ATTR_BRIGHTNESS]
        elif self.brightness is not None:
            payload["brightness"] = self.brightness

        if ATTR_RGB_COLOR in kwargs:
            payload["rgb_color"] = list(kwargs[ATTR_RGB_COLOR])
        elif self.rgb_color is not None:
            payload["rgb_color"] = list(self.rgb_color)

        response = await self.api.async_set_entity(self.regsens_device_id, self.regsens_entity_id, payload)
        self.coordinator.async_apply_entity_state(
            self.regsens_device_id,
            self.regsens_entity_id,
            response.get("value", payload),
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        payload = {"state": "OFF"}
        response = await self.api.async_set_entity(self.regsens_device_id, self.regsens_entity_id, payload)
        self.coordinator.async_apply_entity_state(
            self.regsens_device_id,
            self.regsens_entity_id,
            response.get("value", payload),
        )
