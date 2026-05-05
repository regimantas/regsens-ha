from __future__ import annotations

import logging

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

