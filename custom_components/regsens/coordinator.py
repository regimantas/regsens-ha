from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RegSensApi, RegSensApiError
from .const import DOMAIN, SCAN_INTERVAL, WEBSOCKET_RECONNECT_INTERVAL

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
        self._websocket_task: asyncio.Task | None = None

    async def _async_update_data(self) -> list[dict]:
        try:
            return await self.api.async_get_devices()
        except RegSensApiError as err:
            raise UpdateFailed(str(err)) from err

    def async_start_websocket(self) -> None:
        if self._websocket_task is not None and not self._websocket_task.done():
            return
        self._websocket_task = self.hass.async_create_task(self._async_websocket_loop())

    def async_stop_websocket(self) -> None:
        if self._websocket_task is None:
            return
        self._websocket_task.cancel()
        self._websocket_task = None

    async def _async_websocket_loop(self) -> None:
        while True:
            try:
                async with self.api.session.ws_connect(
                    self.api.websocket_url,
                    headers=self.api.auth_headers,
                    heartbeat=30,
                    timeout=15,
                ) as websocket:
                    _LOGGER.info("Connected to RegSens websocket")
                    async for message in websocket:
                        if message.type == aiohttp.WSMsgType.TEXT:
                            self._handle_websocket_payload(message.json())
                        elif message.type == aiohttp.WSMsgType.ERROR:
                            raise RegSensApiError(f"RegSens websocket error: {websocket.exception()}")
            except asyncio.CancelledError:
                raise
            except Exception as err:
                _LOGGER.warning(
                    "RegSens websocket disconnected, reconnecting in %s seconds: %s",
                    WEBSOCKET_RECONNECT_INTERVAL,
                    err,
                )

            await asyncio.sleep(WEBSOCKET_RECONNECT_INTERVAL)

    def _handle_websocket_payload(self, payload: dict[str, Any]) -> None:
        event_type = str(payload.get("type") or "")
        devices = payload.get("devices")
        if event_type not in {"snapshot", "devices_updated"} or not isinstance(devices, list):
            _LOGGER.debug("Ignoring RegSens websocket payload: %s", payload)
            return
        self.async_set_updated_data(devices)

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
