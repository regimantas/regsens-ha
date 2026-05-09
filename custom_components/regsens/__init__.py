from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_API_KEY, CONF_API_URL, DEFAULT_API_URL, DOMAIN, PLATFORMS
from .api import RegSensApi
from .coordinator import RegSensDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    api_url = entry.data.get(CONF_API_URL, DEFAULT_API_URL)
    api = RegSensApi(api_url, entry.data[CONF_API_KEY], session)
    coordinator = RegSensDataUpdateCoordinator(hass, entry, api)

    await coordinator.async_config_entry_first_refresh()
    coordinator.async_start_websocket()
    entry.async_on_unload(coordinator.async_stop_websocket)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id, None)
        if data:
            data["coordinator"].async_stop_websocket()
    return unload_ok
