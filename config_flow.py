from __future__ import annotations

import aiohttp


class RegSensApiError(Exception):
    pass


class RegSensApi:
    def __init__(self, api_url: str, api_key: str) -> None:
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key

    @property
    def headers(self) -> dict[str, str]:
        return {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    async def async_get_devices(self) -> list[dict]:
        url = f"{self.api_url}/api/v1/devices"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, timeout=15) as resp:
                if resp.status >= 400:
                    raise RegSensApiError(f"API returned HTTP {resp.status}")
                data = await resp.json()
        return data.get("devices", [])

    async def async_set_entity(self, device_id: str, entity_id: str, value):
        url = f"{self.api_url}/api/v1/devices/{device_id}/entities/{entity_id}/set"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json={"value": value}, timeout=15) as resp:
                if resp.status >= 400:
                    raise RegSensApiError(f"API returned HTTP {resp.status}")
                return await resp.json()
