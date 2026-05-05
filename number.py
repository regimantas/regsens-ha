from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_API_URL, CONF_API_KEY, PLATFORMS
from .api import RegSensApi


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = RegSensApi(entry.data[CONF_API_URL], entry.data[CONF_API_KEY])
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"api": api, "devices": []}

    # Initial device fetch. Platforms will also fetch if needed.
    try:
        hass.data[DOMAIN][entry.entry_id]["devices"] = await api.async_get_devices()
    except Exception:
        hass.data[DOMAIN][entry.entry_id]["devices"] = []

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
