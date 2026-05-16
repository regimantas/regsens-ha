from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntry

from .const import CONF_API_KEY, CONF_API_URL, DEFAULT_API_URL, DOMAIN, PLATFORMS
from .api import RegSensApi, RegSensApiError
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


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device_entry: DeviceEntry,
) -> bool:
    """Allow device removal from Home Assistant and mirror it to RegSens."""
    identifiers = {
        identifier
        for identifier in device_entry.identifiers
        if identifier[0] == DOMAIN and identifier[1]
    }
    if not identifiers:
        return False

    device_id = next(iter(identifiers))[1]
    data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if data is None:
        return False

    coordinator: RegSensDataUpdateCoordinator = data["coordinator"]

    if not coordinator.has_device(device_id):
        coordinator.async_remove_device(device_id)
        return True

    try:
        await data["api"].async_delete_device(device_id)
    except RegSensApiError:
        await coordinator.async_request_refresh()
        if coordinator.has_device(device_id):
            return False

    coordinator.async_remove_device(device_id)

    return True
