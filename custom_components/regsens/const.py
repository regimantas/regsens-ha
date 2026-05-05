from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "regsens"

CONF_API_URL = "api_url"
CONF_API_KEY = "api_key"

PLATFORMS = [
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
]

SCAN_INTERVAL = timedelta(seconds=30)
