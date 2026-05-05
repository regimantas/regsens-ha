from __future__ import annotations

from typing import Any

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RegSensDataUpdateCoordinator


class RegSensEntity(CoordinatorEntity[RegSensDataUpdateCoordinator]):
    """Base RegSens entity backed by the shared coordinator."""

    def __init__(
        self,
        coordinator: RegSensDataUpdateCoordinator,
        device: dict[str, Any],
        entity: dict[str, Any],
    ) -> None:
        super().__init__(coordinator)
        self.device = device
        self.entity = entity
        self.device_id = str(device.get("id"))
        self.entity_id = str(entity.get("id"))
        self._attr_name = f"{device.get('name')} {entity.get('name')}"
        self._attr_unique_id = f"regsens_{self.device_id}_{self.entity_id}"

    @property
    def current_entity(self) -> dict[str, Any] | None:
        for device in self.coordinator.data or []:
            if str(device.get("id")) != self.device_id:
                continue

            self.device = device
            for entity in device.get("entities", []):
                if str(entity.get("id")) == self.entity_id:
                    self.entity = entity
                    return entity

        return None

    @property
    def available(self) -> bool:
        return super().available and self.current_entity is not None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self.device.get("name"),
            "manufacturer": self.device.get("manufacturer", "RegSens"),
            "model": self.device.get("model", "RegSens Device"),
        }

