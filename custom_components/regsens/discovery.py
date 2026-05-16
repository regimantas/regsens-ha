from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import RegSensDataUpdateCoordinator
from .entity import RegSensEntity

_LOGGER = logging.getLogger(__name__)


def async_setup_regsens_entities(
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    coordinator: RegSensDataUpdateCoordinator,
    entity_type: str,
    create_entity: Callable[[dict[str, Any], dict[str, Any]], RegSensEntity],
) -> None:
    """Add existing entities and subscribe for newly discovered entities."""

    known_entities: set[tuple[str, str]] = set()

    @callback
    def _discover_entities() -> None:
        new_entities: list[RegSensEntity] = []
        matching_entities = 0
        current_entities: set[tuple[str, str]] = set()

        for device in coordinator.data or []:
            device_id = device.get("id")
            if device_id is None:
                continue

            for entity in device.get("entities", []):
                if entity.get("type") != entity_type:
                    continue

                matching_entities += 1
                entity_id = entity.get("id")
                if entity_id is None:
                    continue

                key = (str(device_id), str(entity_id))
                current_entities.add(key)
                if key in known_entities:
                    continue

                known_entities.add(key)
                new_entities.append(create_entity(device, entity))

        known_entities.intersection_update(current_entities)

        if new_entities:
            _LOGGER.info(
                "RegSens %s discovery added %d new entities",
                entity_type,
                len(new_entities),
            )
            async_add_entities(new_entities)
        else:
            _LOGGER.debug(
                "RegSens %s discovery saw %d matching entities and no new entities",
                entity_type,
                matching_entities,
            )

    _discover_entities()
    entry.async_on_unload(coordinator.async_add_listener(_discover_entities))
