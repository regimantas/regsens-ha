from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
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
        self._attr_has_entity_name = True
        self._attr_name = str(entity.get("name") or self.entity_id)
        self._attr_unique_id = f"regsens_{self.device_id}_{self.entity_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            name=str(device.get("name") or self.device_id),
            manufacturer=str(device.get("manufacturer") or "RegSens"),
            model=str(device.get("model") or "RegSens Device"),
        )

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
