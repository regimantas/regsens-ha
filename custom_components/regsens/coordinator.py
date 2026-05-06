from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RegSensApi, RegSensApiError
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class RegSensDataUpdateCoordinator(DataUpdateCoordinator[list[dict]]):
    """Fetch RegSens devices for all entities in one poll."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: RegSensApi,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=SCAN_INTERVAL,
            always_update=False,
        )
        self.api = api

    async def _async_update_data(self) -> list[dict]:
        try:
            return await self.api.async_get_devices()
        except RegSensApiError as err:
            raise UpdateFailed(str(err)) from err

    def async_apply_entity_state(self, device_id: str, entity_id: str, state: Any) -> None:
        """Apply a just-sent command locally so HA UI does not bounce."""
        changed = False
        devices: list[dict] = []

        for device in self.data or []:
            new_device = dict(device)
            entities: list[dict] = []

            for entity in device.get("entities", []):
                new_entity = dict(entity)
                if str(device.get("id")) == device_id and str(entity.get("id")) == entity_id:
                    new_entity["state"] = state
                    changed = True
                entities.append(new_entity)

            new_device["entities"] = entities
            devices.append(new_device)

        if changed:
            self.async_set_updated_data(devices)
