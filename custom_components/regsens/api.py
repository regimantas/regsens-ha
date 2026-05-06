from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class RegSensApiError(Exception):
    pass


class RegSensApi:
    def __init__(
        self,
        api_url: str,
        api_key: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.session = session

    @property
    def headers(self) -> dict[str, str]:
        return {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    async def async_get_devices(self) -> list[dict]:
        url = f"{self.api_url}/api/v1/devices"
        try:
            async with self.session.get(url, headers=self.headers, timeout=15) as resp:
                if resp.status >= 400:
                    raise RegSensApiError(f"API returned HTTP {resp.status}")
                data = await resp.json()
        except (TimeoutError, aiohttp.ClientError) as err:
            raise RegSensApiError(f"Cannot connect to RegSens API: {err}") from err

        devices = data.get("devices", [])
        entity_count = sum(len(device.get("entities", [])) for device in devices)
        if not devices:
            _LOGGER.warning("RegSens API returned no devices for this API key")
        else:
            _LOGGER.info("RegSens API returned %d devices and %d entities", len(devices), entity_count)
        return devices

    async def async_set_entity(self, device_id: str, entity_id: str, value: Any):
        url = f"{self.api_url}/api/v1/devices/{device_id}/entities/{entity_id}/set"
        try:
            async with self.session.post(
                url,
                headers=self.headers,
                json={"value": value},
                timeout=15,
            ) as resp:
                if resp.status >= 400:
                    raise RegSensApiError(f"API returned HTTP {resp.status}")
                return await resp.json()
        except (TimeoutError, aiohttp.ClientError) as err:
            raise RegSensApiError(f"Cannot connect to RegSens API: {err}") from err
