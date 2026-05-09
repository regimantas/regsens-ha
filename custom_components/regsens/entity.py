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
        self._regsens_device_id = str(device.get("id"))
        self._regsens_entity_id = str(entity.get("id"))
        self._attr_has_entity_name = True
        self._attr_name = str(entity.get("name") or self._regsens_entity_id)
        self._attr_unique_id = f"regsens_{self._regsens_device_id}_{self._regsens_entity_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._regsens_device_id)},
            name=str(device.get("name") or self._regsens_device_id),
            manufacturer=str(device.get("manufacturer") or "RegSens"),
            model=str(device.get("model") or "RegSens Device"),
            configuration_url=coordinator.api.api_url,
        )

    @property
    def regsens_device_id(self) -> str:
        return self._regsens_device_id

    @property
    def regsens_entity_id(self) -> str:
        return self._regsens_entity_id

    @property
    def current_entity(self) -> dict[str, Any] | None:
        for device in self.coordinator.data or []:
            if str(device.get("id")) != self._regsens_device_id:
                continue

            self.device = device
            for entity in device.get("entities", []):
                if str(entity.get("id")) == self._regsens_entity_id:
                    self.entity = entity
                    return entity

        return None

    @property
    def available(self) -> bool:
        if not super().available or self.current_entity is None:
            return False
        if self._regsens_entity_id == "online":
            return True
        for entity in self.device.get("entities", []):
            if str(entity.get("id")) == "online":
                return bool(entity.get("state"))
        return True
