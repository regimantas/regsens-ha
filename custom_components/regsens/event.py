from __future__ import annotations

from typing import Any

from homeassistant.components.event import EventDeviceClass, EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .discovery import async_setup_regsens_entities
from .entity import RegSensEntity

DEFAULT_EVENT_TYPES = [
    "press",
    "single_press",
    "double_press",
    "long_press",
    "hold",
    "release",
    "motion",
    "claim",
    "reconnect",
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    async_setup_regsens_entities(
        entry,
        async_add_entities,
        coordinator,
        "event",
        lambda dev, ent: RegSensEvent(coordinator, dev, ent),
    )


class RegSensEvent(RegSensEntity, EventEntity):
    def __init__(self, coordinator, device: dict[str, Any], entity: dict[str, Any]) -> None:
        super().__init__(coordinator, device, entity)
        self._last_event_key = self._event_key(entity)
        self._attr_event_types = self._event_types(entity)
        self._attr_device_class = self._event_device_class(entity)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(self.coordinator.async_add_listener(self._handle_coordinator_update))

    @callback
    def _handle_coordinator_update(self) -> None:
        entity = self.current_entity
        if entity is None:
            return

        event = self._parse_event(entity)
        if event is None:
            self.async_write_ha_state()
            return

        event_key = self._event_key(entity)
        if event_key == self._last_event_key:
            self.async_write_ha_state()
            return

        self._last_event_key = event_key
        event_type, event_data = event
        if event_type not in self._attr_event_types:
            self._attr_event_types = [*self._attr_event_types, event_type]
        self._trigger_event(event_type, event_data)
        self.async_write_ha_state()

    @staticmethod
    def _event_types(entity: dict[str, Any]) -> list[str]:
        values: list[str] = []
        for key in ("event_types", "options"):
            raw_values = entity.get(key)
            if isinstance(raw_values, list):
                values.extend(str(value).strip() for value in raw_values)

        values.extend(DEFAULT_EVENT_TYPES)
        return list(dict.fromkeys(value for value in values if value))

    @staticmethod
    def _event_device_class(entity: dict[str, Any]) -> EventDeviceClass | None:
        value = str(entity.get("device_class") or "").strip()
        if not value:
            entity_id = str(entity.get("id") or "").lower()
            name = str(entity.get("name") or "").lower()
            if "motion" in entity_id or "motion" in name:
                value = EventDeviceClass.MOTION
            elif "button" in entity_id or "button" in name:
                value = EventDeviceClass.BUTTON

        if not value:
            return None
        try:
            return EventDeviceClass(value)
        except ValueError:
            return None

    @staticmethod
    def _parse_event(entity: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
        state = entity.get("state")
        if state is None or state is False:
            return None

        event_type = ""
        event_data: dict[str, Any] = {}

        if isinstance(state, str):
            event_type = state.strip()
        elif isinstance(state, dict):
            event_type = str(
                state.get("event_type")
                or state.get("type")
                or state.get("event")
                or state.get("action")
                or ""
            ).strip()
            event_data = {
                str(key): value
                for key, value in state.items()
                if key not in {"event_type", "type", "event", "action"}
            }
        elif state is True:
            event_type = str(entity.get("event_type") or "press").strip()

        if not event_type:
            return None

        return event_type, event_data

    @staticmethod
    def _event_key(entity: dict[str, Any]) -> Any:
        state = entity.get("state")
        if isinstance(state, dict):
            return (
                state.get("id")
                or state.get("event_id")
                or state.get("timestamp")
                or tuple(sorted((str(key), repr(value)) for key, value in state.items()))
            )
        return state
